# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajarjestelma partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi


#!/usr/bin/python


from django.db import models
from random import uniform
from TulosLaskin import *
import settings

import thread
import time 

from binascii import *
import sys

class Kipa(models.Model):
        # code between "#gen_dia_class xxx"-> "#end_dia_class" tags is autogenerated from tietokanta.dia"
        # for these parts only make changes to data table definitions in tietokanta.dia!
        #gen_dia_class Kipa

        versio = models.IntegerField()

        #end_dia_class
        class Meta:
                db_table = "versio"


class Kisa(models.Model) :
        # code between "#gen_dia_class xxx"-> "#end_dia_class" tags is autogenerated from tietokanta.dia"
        # for these parts only make changes to data table definitions in tietokanta.dia!
        #gen_dia_class Kisa

        nimi = models.CharField(max_length=255)
        aika = models.CharField(max_length=255, blank=True, null=True )
        paikka = models.CharField(max_length=255, blank=True )
        tunnistus = models.BooleanField()

        #end_dia_class
        def __unicode__(self) :
                return self.nimi

        class Meta:
                verbose_name_plural = "Kisat"
                db_table = u"kipa_kisa"

class Sarja(models.Model) :
        # code between "#gen_dia_class xxx"-> "#end_dia_class" tags is autogenerated from tietokanta.dia"
        # for these parts only make changes to data table definitions in tietokanta.dia!
        #gen_dia_class Sarja

        nimi = models.CharField(max_length=255)
        vartion_maksimikoko = models.IntegerField(blank=True, null=True, default=0 )
        vartion_minimikoko = models.IntegerField(blank=True, null=True,default=0 )
        kisa = models.ForeignKey(Kisa)
        tasapiste_teht1 = models.IntegerField(blank=True, null=True )
        tasapiste_teht2 = models.IntegerField(blank=True, null=True )
        tasapiste_teht3 = models.IntegerField(blank=True, null=True )

        #end_dia_class
        def __unicode__(self) :
                return self.kisa.nimi+"."+self.nimi
        
        def save(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                #self.tuloksetUusiksi()
                super(Sarja,self).save(*args,**kwargs)
        def delete(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                #self.tuloksetUusiksi()
                super(Sarja,self).delete(*args,**kwargs)

        def laskeTulokset(self) :
                """
                cacheName = str(self.kisa.id)+'_'+str(self.id)+'_tulokset'
                laskeeName = str(self.kisa.id)+'_'+str(self.id)+'_laskee'
                laskee=cache.get( laskeeName ) 
                if settings.TAUSTALASKENTA:
                   while laskee : # Odotetaan että toinen threadi laskee tulokset
                        time.sleep(0.4) # Tarkistetaan 400ms välein
                        laskee=cache.get( laskeeName ) 
                tulokset=cache.get( cacheName )
                if not tulokset or not settings.CACHE_TULOKSET : # ei cachea -> lasketaan
                        cache.set( cacheName , 0 ) # Tunnistetaan laskennanaikainen tallennus
                        cache.set( laskeeName , True , 30) # Merkitään laskennan olevan käynnissä
                        tulokset = laskeSarja(self) 
                        cache.delete( laskeeName ) # Merkitään laskennan olevan valmis
                        ctulos = cache.get( cacheName ) # Muutoksia laskennan aikana 
                        if ctulos == None :  return tulokset # Jätetään cacheamatta.
                # Asetetaan cache.
                cache.set( cacheName , tulokset, settings.CACHE_TULOKSET_TIME)
                """
                syotteet=Syote.objects.filter(maarite__osa_tehtava__tehtava__sarja=self)
                if syotteet: onjoo=1 # Pakotetaan syotteiden haku tähän.
                tulokset = laskeSarja(self,syotteet) 
                return tulokset
        
        
        def taustaTulokset(self) :
                pakkotehtajotain=1
                #if settings.TAUSTALASKENTA: # Tulosten laskenta taustalla threadissa.
                #        laskeeName = str(self.kisa.id)+'_'+str(self.id)+'_laskee'
                #        laskee=cache.get( laskeeName ) # Tarkistetaan ollaanko tuloksia jo laskemassa.
                #        if not laskee:  thread.start_new_thread( self.laskeTulokset,() )
        
        def tuloksetUusiksi(self) :
                # Poistetaan tulosten cache
                pakkotehdajotain=1
                #cacheName = str(self.kisa.id)+'_'+str(self.id)+'_tulokset'
                #cache.delete(cacheName)
        
        class Meta:
                verbose_name_plural = "Sarjat"
                db_table = u"kipa_sarja"       


class Vartio(models.Model) :
        # code between "#gen_dia_class xxx"-> "#end_dia_class" tags is autogenerated from tietokanta.dia"
        # for these parts only make changes to data table definitions in tietokanta.dia!
        #gen_dia_class Vartio

        nro = models.IntegerField()
        nimi = models.CharField(max_length=255)
        sarja = models.ForeignKey(Sarja)
        piiri = models.CharField(max_length=255, blank=True )
        lippukunta = models.CharField(max_length=255, blank=True )
        puhelinnro = models.CharField(max_length=255, blank=True )
        sahkoposti = models.CharField(max_length=255, blank=True )
        osoite = models.CharField(max_length=255, blank=True )
        keskeyttanyt = models.IntegerField(blank=True, null=True )
        ulkopuolella = models.IntegerField(blank=True , null=True )

        #end_dia_class

        def save(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                self.sarja.tuloksetUusiksi()
                super(Vartio,self).save(*args,**kwargs)

        def delete(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                self.sarja.tuloksetUusiksi()
                super(Vartio,self).delete(*args,**kwargs)
        
        def __unicode__(self) :
                return self.sarja.kisa.nimi+"."+self.sarja.nimi+"."+str(self.nro)
        class Meta:
                verbose_name_plural = "Vartiot"
                db_table = u"kipa_vartio"

class Henkilo(models.Model) :
        # code between "#gen_dia_class xxx"-> "#end_dia_class" tags is autogenerated from tietokanta.dia"
        # for these parts only make changes to data table definitions in tietokanta.dia!
        #gen_dia_class Henkilo

        nimi = models.CharField(max_length=255)
        syntymavuosi = models.IntegerField(blank=True , null=True )
        lippukunta = models.CharField(max_length=255, blank=True, null=True )
        jasennumero = models.CharField(max_length=15, blank=True, null=True )
        puhelin_nro = models.CharField(max_length=15, blank=True, null=True )
        homma = models.CharField(max_length=255, blank=True, null=True )

        #end_dia_class
        def __unicode__(self) :
                return self.nimi
        class Meta:
                verbose_name_plural = "Henkilot"
                db_table = u"kipa_henkilo"

class Tehtava(models.Model) :
        # code between "#gen_dia_class xxx"-> "#end_dia_class" tags is autogenerated from tietokanta.dia"
        # for these parts only make changes to data table definitions in tietokanta.dia!
        #gen_dia_class Tehtava

        nimi = models.CharField(max_length=255)
        lyhenne = models.CharField(max_length=255)
        tehtavaryhma = models.CharField(max_length=255, blank=True )
        tehtavaluokka = models.CharField(max_length=255, blank=True )
        rastikasky = models.TextField(blank=True )
        jarjestysnro = models.IntegerField()
        kaava = models.CharField(max_length=255)
        sarja = models.ForeignKey(Sarja)
        tarkistettu = models.BooleanField()
        maksimipisteet = models.CharField(max_length=255)
        svirhe = models.BooleanField()

        #end_dia_class
        def mukanaOlevatVartiot(self):
                """
                Palauttaa listan Vartioista jotka ovat mukana tehtavan interpoloinneissa.
                """
                vartiot = self.sarja.vartio_set.all()
                mukana = []
                if vartiot:
                        for v in vartiot:
                                laskennassa = True
                                if not v.ulkopuolella==None:
                                        if self.jarjestysnro >= v.ulkopuolella:
                                                laskennassa = False
                                if not v.keskeyttanyt == None :
                                        if self.jarjestysnro >= v.keskeyttanyt:
                                                laskennassa = False
                                if laskennassa : 
                                        mukana.append(v)
                return mukana

        def save(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                self.sarja.tuloksetUusiksi()
                super(Tehtava,self).save(*args,**kwargs)

        def delete(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                self.sarja.tuloksetUusiksi()
                super(Tehtava,self).delete(*args,**kwargs)
        
        def __unicode__(self) :
                sarja = self.sarja
                kisa = sarja.kisa
                return kisa.nimi+"."+ sarja.nimi+"."+ self.nimi
        class Meta:
                ordering=("jarjestysnro",)
                verbose_name_plural = "Tehtavat"
                db_table = u"kipa_tehtava"


class OsaTehtava(models.Model) :
        OSA_TYYPIT=(    ("kp","kisapisteita"),
                        ("rp","raakapisteita"),
                        ("ka","kokonaisaika"),
                        ("ala","alkuaika ja loppuaika"),
                        ("vk","vapaa kaava"), )
        # code between "#gen_dia_class xxx"-> "#end_dia_class" tags is autogenerated from tietokanta.dia"
        # for these parts only make changes to data table definitions in tietokanta.dia!
        #gen_dia_class OsaTehtava

        nimi = models.CharField(max_length=255)
        tyyppi = models.CharField(max_length=255, choices = OSA_TYYPIT )
        kaava = models.CharField(max_length=255)
        tehtava = models.ForeignKey(Tehtava)

        #end_dia_class
        def save(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                self.tehtava.sarja.tuloksetUusiksi()
                super(OsaTehtava,self).save(*args,**kwargs)

        def delete(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                self.tehtava.sarja.tuloksetUusiksi()
                super(OsaTehtava,self).delete(*args,**kwargs)

        def __unicode__(self) :
                tehtava= self.tehtava
                sarja = tehtava.sarja
                kisa = sarja.kisa
                return kisa.nimi+"."+ sarja.nimi+"."+ tehtava.nimi+"."+self.nimi
        class Meta:
                verbose_name_plural = "Osatehtavat"
                ordering = ["nimi"]
                db_table = u"kipa_osatehtava"

class SyoteMaarite(models.Model) :
        TYYPPI_VAIHTOEHDOT = (
                ('aika', 'aika'),
                ('piste', 'piste'),)

        # code between "#gen_dia_class xxx"-> "#end_dia_class" tags is autogenerated from tietokanta.dia"
        # for these parts only make changes to data table definitions in tietokanta.dia!
        #gen_dia_class SyoteMaarite

        nimi = models.CharField(max_length=255)
        tyyppi = models.CharField(max_length=255, choices=TYYPPI_VAIHTOEHDOT )
        kali_vihje = models.CharField(max_length=255, blank=True , null=True )
        osa_tehtava = models.ForeignKey(OsaTehtava)

        #end_dia_class
        def save(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                self.osa_tehtava.tehtava.sarja.tuloksetUusiksi()
                super(SyoteMaarite,self).save(*args,**kwargs)

        def delete(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                self.osa_tehtava.tehtava.sarja.tuloksetUusiksi()
                super(SyoteMaarite,self).delete(*args,**kwargs)

        def __unicode__(self) :
                ot = self.osa_tehtava
                tehtava= ot.tehtava
                sarja = tehtava.sarja
                kisa = sarja.kisa
                return kisa.nimi+"."+ sarja.nimi+"."+ tehtava.nimi+"."+ot.nimi+"."+self.nimi
        class Meta:
                ordering = ['osa_tehtava','nimi']
                verbose_name_plural = "Syotteen maaritteet"
                db_table = u"kipa_syotemaarite"

class Syote(models.Model) :
        # code between "#gen_dia_class xxx"-> "#end_dia_class" tags is autogenerated from tietokanta.dia"
        # for these parts only make changes to data table definitions in tietokanta.dia!
        #gen_dia_class Syote

        arvo = models.CharField(max_length=255, blank = True, null=True )
        vartio = models.ForeignKey(Vartio, blank=True, null=True )
        maarite = models.ForeignKey(SyoteMaarite)
        tarkistus = models.CharField(max_length=255, blank=True,null=True )

        #end_dia_class
        def save(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                self.vartio.sarja.tuloksetUusiksi()
                super(Syote,self).save(*args,**kwargs)

        def delete(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                self.vartio.sarja.tuloksetUusiksi()
                super(Syote,self).delete(*args,**kwargs)

        def __unicode__(self) :
                vartio = self.vartio
                maarite=self.maarite
                ot = maarite.osa_tehtava
                tehtava= ot.tehtava
                sarja = tehtava.sarja
                kisa = sarja.kisa
                return kisa.nimi+"."+ sarja.nimi+"."+ tehtava.nimi+"."+ot.nimi+"."+maarite.nimi+"."+str(vartio.nro)
        class Meta:
                verbose_name_plural = "Syotteet"
                db_table = u"kipa_syote"


class TulosTaulu(models.Model) :
        # code between "#gen_dia_class xxx"-> "#end_dia_class" tags is autogenerated from tietokanta.dia"
        # for these parts only make changes to data table definitions in tietokanta.dia!
        #gen_dia_class TulosTaulu

        vartio = models.ForeignKey(Vartio)
        tehtava = models.ForeignKey(Tehtava)
        pisteet = models.CharField(max_length=255)

        #end_dia_class
        def save(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                self.vartio.sarja.tuloksetUusiksi()
                super(TulosTaulu,self).save(*args,**kwargs)
        
        def delete(self,*args,**kwargs) : # Tulokset uusiksi tallennuksen yhteydessä
                self.vartio.sarja.tuloksetUusiksi()
                super(TulosTaulu,self).delete(*args,**kwargs)

        def __unicode__(self) :
                tehtava= self.tehtava
                sarja = tehtava.sarja
                kisa = sarja.kisa
                return kisa.nimi+"."+ sarja.nimi+"."+ tehtava.nimi +"."+ str(self.vartio.nro)
        class Meta:
                abstract = True
                db_table = u"kipa_tulostaulu"

class TuomarineuvosTulos(TulosTaulu) :
        class Meta :
                verbose_name_plural = "Tuomarineuvoston tulokset"
                db_table = "kipa_tuomarineuvostulos"

class TestausTulos(TulosTaulu):
        class Meta:
                verbose_name_plural = "Testattavat tulokset"
                db_table = u'kipa_testaustulos'

class Parametri(models.Model) :
        # code between "#gen_dia_class xxx"-> "#end_dia_class" tags is autogenerated from tietokanta.dia"
        # for these parts only make changes to data table definitions in tietokanta.dia!
        #gen_dia_class Parametri

        nimi = models.CharField(max_length=255)
        arvo = models.CharField(max_length=255)
        osa_tehtava = models.ForeignKey(OsaTehtava)

        #end_dia_class
        class Meta:
                verbose_name_plural = "OsaTehtavan paramentrit" 
                db_table = u'kipa_parametri'

        def __unicode__(self):
                ot = self.osa_tehtava
                tehtava= ot.tehtava
                sarja = tehtava.sarja
                kisa = sarja.kisa
                return kisa.nimi+"."+ sarja.nimi+"."+ tehtava.nimi+"."+ot.nimi+"."+self.nimi

