#!/usr/bin/python3

import http.client
from tkinter import *
import xml.etree.ElementTree as etree
import socket
import re
import sys
import time
import base64
import os
from wakeonlan import wol
sonyTv = {}
dialogMsg =""
headers = {"Content-Type": "application/atom+xml"}

sonyTv["pairingKey"] = sys.argv[3]
if sonyTv["pairingKey"] != ":0000" : sonyTv["pairingKey"] = base64.b64encode(sonyTv["pairingKey"].encode("utf-8")).decode("utf-8")

sonyTv["mac"] = sys.argv[4]

sonyTv["ipaddress"] = sys.argv[2]

result = str(sys.argv[1])

def testFichierCookie():
    fichierExiste = False
    try:
        with open(os.path.dirname(os.path.abspath(__file__))+'\leCookie.txt'): pass
        #print('Le fichier existe')
        fichierExiste = True
    except IOError:
        print("Le fichier du Cookie n'existe pas.")
    return fichierExiste

def lectureCookie():
    file = open(os.path.dirname(os.path.abspath(__file__))+'\leCookie.txt', 'r')
    leCookie = file.read()
    file.close()
    return leCookie

def ecritureCookie(texte):
    file = open(os.path.dirname(os.path.abspath(__file__))+'\leCookie.txt', "w")
    file.write(texte)
    file.close()
    return 0
    
def majCookie():
    if testFichierCookie():
        leCookie = lectureCookie()
        if len(leCookie) < 10 :
            print("Le Cookie semble avarié : " + leCookie + ", je demande un nouveau Cookie")
            leCookie = getCookie()
            if leCookie == 0 or not leCookie :
                print("Je ne parviens pas à obtenir de nouveau Cookie..")
            else :
                ecritureCookie(leCookie)
        else :
            #print("Le cookie semble OK : " + leCookie)
            return leCookie
      
    else:
        print("Fichier Cookie introuvable, je demande un nouveau Cookie")
        leCookie = getCookie()
        if leCookie == 0 :
            print("Je ne parviens pas à obtenir de nouveau Cookie..")
        else :
            ecritureCookie(leCookie)
    return leCookie
        
def testOn():
    print("Je teste si la télé est allumée..")

    allumee = False

    try:
        conn = http.client.HTTPConnection(sonyTv["ipaddress"],52323,timeout=5)
        #conn.request('HEAD', '/')
        #conn.request("POST", "/sony/accessControl")
        conn.request("GET","/dmr.xml")
        res = conn.getresponse()
        #print(res.status)
        print(res.reason)
        if res.status == 200 : allumee = True
    except:
        print("Je ne parviens pas à joindre la télé..")

    return allumee

def getCookie():
    conn = http.client.HTTPConnection(sonyTv["ipaddress"])
    pairCmd = """{"method":"actRegister","params":[{"clientid":"Sarah","nickname":"SARAH","level":"private"},[{"value":"yes","function":"WOL"}]],"id":9,"version":"1.0"}"""
    conn.request("POST", "/sony/accessControl", pairCmd, headers=headers)
    httpResponse = conn.getresponse()
    if httpResponse.reason != "OK" :
        if httpResponse.reason == "Unauthorized" :
            if sonyTv["pairingKey"]==":0000" :
                print("_______________________")
                print(" PROCEDURE D'APPAIRAGE ")
                print("-----------------------")
                print(">> Vous avez 60 sec  <<")
                print("Saissez le code affiché sur la TV dans la config du module.")
                print("... puis relancez une commande ('Sarah met la télé plus fort' par exemple)")
                sys.exit(0) 
            else :
                print("Je procède à l'appairage avec le code saisi dans la configuration du module")
                return setPairingKey(sonyTv["pairingKey"])
        else:
            print("Erreur de renouvellement de Cookie : " + httpResponse.reason)
        return 0
    return httpResponse.getheader('Set-Cookie')

def setPairingKey(code):
    headers = {
        "User-Agent": "Dalvik/1.6.0 (Linux; U; Android 4.4.2; HTC Sensation Build/KVT49L)",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
        "Authorization": "Basic %s" % code
    }
    content = """{"method":"actRegister","params":[{"clientid":"Sarah","nickname":"SARAH","level":"private"},[{"value":"yes","function":"WOL"}]],"id":9,"version":"1.0"}"""
    url = '/sony/accessControl'
    conn = http.client.HTTPConnection(sonyTv["ipaddress"])
    conn.request("POST",url, content, headers=headers)
    httpResponse = conn.getresponse()
    return httpResponse.getheader('Set-Cookie')

def handleCommand(cmdcode):
    headers = {
    'User-Agent': 'TVSideView/2.0.1 CFNetwork/672.0.8 Darwin/14.0.0',
    'Content-Type': 'text/xml; charset=UTF-8',
    'SOAPACTION': '"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    "Cookie": theCookie,
    "Cookie pair": theCookie
    }
    content = """<?xml version="1.0"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
      <s:Body>
        <u:X_SendIRCC xmlns:u="urn:schemas-sony-com:service:IRCC:1">
          <IRCCCode>"""+cmdcode+"""</IRCCCode>
        </u:X_SendIRCC>
      </s:Body>
    </s:Envelope>"""
    #print("Content : "+content)
    url = '/sony/IRCC'

    conn = http.client.HTTPConnection(sonyTv["ipaddress"])
    conn.request("POST",url, content, headers=headers)
    httpResponse = conn.getresponse()
    #print(httpResponse.status)
    return httpResponse.status


if result =="allume" :
    wol.send_magic_packet(sonyTv["mac"])
    print("Demande d'allumage envoyée.. patientez quelques secondes")
else :
    if testOn():
        print("La télé est bien allumée.")
        theCookie = majCookie()
        if theCookie != 0 :
            print("J'envoie la commande à la TV..")
            if handleCommand(result) != 200 :
                print("La commande n'a pas été reçue. J'efface le Cookie, et je relance la commande..")
                os.remove(os.path.dirname(os.path.abspath(__file__))+'\leCookie.txt')
                theCookie = majCookie()
                if theCookie != 0 :
                    print("J'envoie la commande à la TV..")
                    if handleCommand(result) != 200 :
                        print("La commande n'a pas été reçue. On dirait qu'il y a un problème..")
                    else :
                        print("Commande " + result + " bien reçue par la TV.")
            else :
                print("Commande " + result + " bien reçue par la TV.")
        else :
            print("Aucune commande n'a été envoyée à la TV")

    else :
        print("La télé ne répond pas, j'essaie de l'allumer.. patientez quelques secondes avant de réessayer")
        wol.send_magic_packet(sonyTv["mac"])
