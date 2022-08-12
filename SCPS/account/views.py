from django.contrib.auth.views import LogoutView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework import status, authentication, generics, permissions
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, Node, NodeStation, Neighbor, Allocation, UserNode, Security, SecurityStation, FanCoil
import json
from django.contrib.auth import get_user_model
from django.db import models
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import paho.mqtt.client as mqtt
from .serializers import CustomUserSerializer, LogoutSerializer
import logging
import threading
import time
from django.utils import timezone
from datetime import datetime
# from SCPS import settings

User = get_user_model()

# Create your views here.
client = mqtt.Client()


# redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
#                                   port=settings.REDIS_PORT, db=0)

def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if (gm > 2):
        gy2 = gy + 1
    else:
        gy2 = gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if (days > 365):
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if (days < 186):
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return [jy, jm, jd]


def jalali_to_gregorian(jy, jm, jd):
    jy += 1595
    days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
    if jm < 7:
        days += (jm - 1) * 31
    else:
        days += ((jm - 7) * 30) + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += ((days - 1) // 365)
        days = (days - 1) % 365
    gd = days + 1
    if ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
        kab = 29
    else:
        kab = 28
    sal_a = [0, 31, kab, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    while (gm < 13 and gd > sal_a[gm]):
        gd -= sal_a[gm]
        gm += 1
    return [gy, gm, gd]


def Graphws(z):
    nodes = []
    links = []
    for t in z["graph"]:
        p = {
            'id': str(t["id"])
        }
        nodes.append(p)
        for n in t["neighbor"]:
            o = {
                'source': str(t["id"]),
                'target': str(n["id"])
            }
            links.append(o)
    data = {'graph': nodes, 'links': links}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_test',  # group _ name
        {
            'type': 'graph',
            'message': json.dumps(data)
        }
    )


def errorws(z):
    for t in z["errors"]:
        data = {'node': str(t["id"]), 'color': 'red', 'message': 'Error Code :' + str(t["code"])}
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'error',
                'message': json.dumps(data)
            }
        )


def pychart(z):
    l = 0
    w = 0
    p = 0
    for i in z["data"]:
        l = l + 1
    #for i in z["errors"]:
    #    w = w + 1
    for i in Node.objects.all():
        p = p + 1
    active = ((l - w) / p) * 100
    deactive = (w / p) * 100
    onhold = ((p - l) / p) * 100
    mymessage = []
    l = {'name': 'Group A', 'value': active}
    mymessage.append(l)
    l = {'name': 'Group B', 'value': deactive}
    mymessage.append(l)
    l = {'name': 'Group C', 'value': onhold}
    mymessage.append(l)
    data = mymessage
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_test',  # group _ name
        {
            'type': 'pychart',
            'message': json.dumps(data)
        }
    )


def roomTem(z):
    sum = 0
    counter = 0
    min = 196
    max = 0
    for t in z["data"]:
        sum = sum + float(t["homeT"])
        counter = counter + 1
        if t["homeT"] > max:
            max = t["homeT"]
        if t["homeT"] < min:
            min = t["homeT"]
    Avg = sum / counter
    data = {'date': str(timezone.now()), 'tem': Avg}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_test',  # group _ name
        {
            'type': 'roomTem',
            'message': json.dumps(data)
        }
    )

def minandmax(z):
    sum = 0
    counter = 0
    min = 10000000
    max = 0
    for t in z["data"]:
        sum = sum + float(t["homeT"])
        counter = counter + 1
        if float(t["homeT"]) > max:
            max =float(t["homeT"])
            maxid = "156"
        if float(t["homeT"]) < min:
            min = float(t["homeT"])
            minid = "193"
    Avg = sum / counter
    data = {'id': maxid, 'temp': max}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_test',  # group _ name
        {
            'type': 'maxTemp',
            'message': json.dumps(data)
        }
    )
    data = {'id': minid, 'temp': min}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_test',  # group _ name
        {
            'type': 'minTemp',
            'message': json.dumps(data)
        }
    )


def nodeNewTem(z):
    for t in z["data"]:
        data = {'nodeid': str(t["id"]), 'time': str(timezone.now()), 'temp': t["homeT"]}
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'nodeNewTem',
                'message': json.dumps(data)
            }
        )
        data = [str(t["id"]), "#332525"]
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'nodeColor',
                'message': data
            }
        )


def ReciveMqtt1(z):
    for t in z["graph"]:
        k = Node()
        k.MacAddress = t["id"]
        print(Node.objects.filter(MacAddress=t["id"]).count())
        if Node.objects.filter(MacAddress=t["id"]).count() == 0:
            k.save()
    Neighbor.objects.all().delete()
    for t in z["graph"]:
        nodeid1 = t["id"]
        for n in t["neighbor"]:
            nodeid2 = n["id"]
            rssi = n["rssi"]
            h = Neighbor()
            node1 = Node.objects.get(MacAddress=nodeid1)
            node2 = Node.objects.get(MacAddress=nodeid2)
            h.Node1 = node1
            h.Node2 = node2
            h.RSSI = rssi
            h.save()
            #o = t["nums"]
            #u = 0
            #if Node.objects.filter(MacAddress=nodeid1).count() > o:
            #    o = Node.objects.filter(MacAddress=nodeid1).count() - o
            #while u < o:
            #    l = FanCoil()
            #    l.Node = Node.objects.get(MacAddress=nodeid1)
            #    u = u + 1
            #    l.save()

    Graphws(z)


def ReciveMqtt2(z):
    mynow = timezone.now()
    #    k=gregorian_to_jalali(mynow.year,mynow.month,mynow.day)
    #    now=datetime.now()
    #    now=datetime(k[0],k[1],k[2],mynow.hour,mynow.minute,mynow.second)
    print(z)
    for t in z["data"]:
        nodes = NodeStation()
        nodeid = t["id"]
        try:
            node = Node.objects.get(MacAddress=nodeid)
        except :
            print(t["id"])
        nodes.Node = node
        s = 0
        l = 0
        #FanCoils = FanCoil.objects.get()
        #x = FanCoil.objects.filter(Node=node)
        #for u in t["fancoilT"]:
        #    x[l].Temperature = u
        #    s = s + u
        #    l = l + 1
        #f = s / l
        #for u in t["valveState"]:
        #    x[l].valvstate = u
        nodes.FanCoilTemperature = 154#f
        nodes.HomeTemperature = t["homeT"]
        nodes.Presence = t["present"]
        # nodes.faucetState=t["faucetState"]
        nodes.SetPointTemperature = t["setT"]
        nodes.DateTime = mynow
        nodes.save()
    # for t in z["errors"]:
    #     node2 = Node.objects.get(MacAddress=t["id"])
    #     node2.ErrorId = t["code"]
    #     node2.save()
    # errorws(z)
    # for t in z["security"]:
    #    Securitys=SecurityStation()
    #   Securitys.Name=t["name"]
    #  Securitys.Value=t["value"]
    # Securitys.save()
    minandmax(z)
    pychart(z)
    roomTem(z)
    nodeNewTem(z)


def on_connect(client, userdata, flags, rc):
    print("Connected to broker!")
    client.subscribe("scps/server")


def on_message(client, userdata, message):
    l = message.payload.decode()
    print(message.payload.decode())
    z = json.loads(l)
    if z["type"] == "01":
        ReciveMqtt1(z)
    if z["type"] == "02":
        ReciveMqtt2(z)


def MqttRun():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('mqtt.giot.ir', 1883)
    client.subscribe("scps/client")
    client.loop_forever()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user: CustomUser):
        token = super().get_token(user)

        token['role'] = user.role
        token['email'] = user.email
        token['password'] = user.password
        token['user_id'] = user.id
        token['user_name'] = user.user_name
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomUserCreate(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format='json'):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlacklistTokenUpdateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(generics.GenericAPIView):
    print("in logout")
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class sendLastData(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        l = NodeStation.objects.all().order_by("DateTime")
        sum = 0
        d = datetime.now()
        counter = 1
        en = 0
        p=[]
        for i in l:
            if d == i.DateTime:
                sum = sum + i.HomeTemperature
                print('sum : ' + str(sum))
                counter = counter + 1
                print('counter : ' + str(counter))
            else:
                if en == 0:
                    d = i.DateTime
                    counter = 1
                    sum = i.HomeTemperature
                    en = 1
                    continue
                Avg = sum / counter
                l={'date': str(d), 'tem': Avg}
                p.append(l)
                channel_layer = get_channel_layer()
                d = i.DateTime
                counter = 1
                sum = i.HomeTemperature
        data=p 
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'roomTem',
                'message': json.dumps(data)
            }
        )
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        NodeArray = Node.objects.all()
        print(str(NodeArray))
        for i in NodeArray:
            if i.MacAddress == request.data["nodeid"]:
                NodeStationArray = NodeStation.objects.filter(Node=i).order_by("DateTime")
                times = []
                temps = []
                for z in NodeStationArray:
                    times.append(str(z.DateTime))
                    temps.append(str(z.HomeTemperature))
                data = {'nodeid': str(i.MacAddress), 'times': times, 'temps': temps}
        return Response(data=data, status=status.HTTP_200_OK)


class SetConfigNode(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        a = 0
        b = 0
        c = -1
        #valve_cammand = []
        dictsend = {}
        MyNode = Node.objects.get(MacAddress=request.data["nodeid"])
        MyNode.SetPointTemperature = request.data["temp"]
        if request.data["fanopen"] == True:
            MyNode.status = True
            a = 1
        elif request.data["fanopen"] == False:
            MyNode.status = False
            a = 0
        if request.data["perm"] == "YES":
            MyNode.ControlStatus = True
            b = 1
        elif request.data["perm"] == "NO":
            MyNode.ControlStatus = False
            b = 0
        if request.data["sleepMode"] == True:
            MyNode.mode = "sleepMode"
            MyNode.status = False
            c = 0
            a = 0
        if request.data["optimalMode"] == True:
            MyNode.mode = "optimalMode"
            c = 1
        if request.data["manualMode"] == True:
            MyNode.mode = "manualMode"
            c = 2
        
    #    NodeArray = Node.objects.all()
    #    print(str(NodeArray))
    #    for i in NodeArray:
    #        if i.MacAddress == request.data["nodeid"]:
    #            NodeStationArray = FanCoil.objects.filter(Node=i)
    #            o = 1
    #            for z in NodeStationArray:
    #                if o > 3:
    #                    o = 3
    #                valve_cammand.append(request.data["cValve" + str(o)])
    #                z.valv = request.data["cValve" + str(o)]
    #                o = o + 1
    #                z.save()
    #    MyNode.save()
        valve_cammand=[]
        fan_command=[]
        if request.data["cValue1"]==True:
            valve_cammand.append(1)
        else:
            valve_cammand.append(0)
    
        if request.data["cValue2"]==True:
            valve_cammand.append(1)
        else:
            valve_cammand.append(0)
        if request.data["fanAir1"]==True:
            fan_command.append(1)
        else:
            fan_command.append(0)
    
        if request.data["fanAir2"]==True :
            fan_command.append(1)
        else:
            fan_command.append(0)
    
        client = mqtt.Client()
        dictsend = {
            "type": "33",
            "time": "568595",
            "conf": [
                {
                    "id": str(MyNode.MacAddress),
                    "setT": [MyNode.SetPointTemperature,255,255,255],
                    "valve_command": valve_cammand,
                    "workmode": c,
                    "permission": b,
                    "hvac": 1,
                    "fan_command": fan_command,
                }
            ],
            "equ": {}
        }
        json_object = json.dumps(dictsend)
        print(json_object)
        client.connect('mqtt.giot.ir', 1883)
        client.publish('scps/server', json_object)
        return Response(status=status.HTTP_200_OK)


class MqttRunCommand(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        x = threading.Thread(target=MqttRun)
        x.start()
        return Response(status=status.HTTP_200_OK)


class graphNodes(APIView):
    permission_classes=[AllowAny]
    def get(self, request):
        nodes = []
        links = []
        for t in Node.objects.all():
            p = {
                'id': str(t.MacAddress)
            }
            nodes.append(p)
            for n in Neighbor.objects.all():
                o = {
                    'source': str(n.Node1.MacAddress),
                    'target': str(n.Node2.MacAddress)
                }
                #links.append(o)
        data = {'graph': nodes, 'links': links}
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'graph',
                'message': json.dumps(data)
            }
        )
        return Response(status=status.HTTP_200_OK)
