from django.conf import settings
from django.shortcuts import render

import speech_recognition as sr
from pydub import AudioSegment
from pytube import *
from moviepy.editor import *
import nltk
import string
import re
from nltk.tokenize import word_tokenize
import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import datetime

from toxic.models import rekapitulasi as rp
from toxic.models import kasar as ks
from toxic.models import saran as srn

def handle_uploaded_file(f, name):
  namafile = 'toxic/AudioFile/'+name
  with open(namafile, 'wb+') as destination:
    for chunk in f.chunks():
      destination.write(chunk)

def konversi(namafile):
  nama_file = 'toxic/AudioFile/'+namafile
  if namafile[-3:] == "mp3":
    sound = AudioSegment.from_mp3(nama_file)
    sound.export('toxic/AudioFile/'+namafile[:-4]+'.wav', format="wav")
    nama_file = 'toxic/AudioFile/'+namafile[:-4]+'.wav'
    return nama_file
  return nama_file

def transkrip(namafile):
  r = sr.Recognizer()
  nama_file = namafile
  with sr.AudioFile(nama_file) as source:
    teks = ''
    audio = r.record(source)
    try:
      teks = r.recognize_google(audio, language='id-ID')
    except:
      teks = 'coba lagi'
  return teks

def perbaikan(namafile):
  isifile = namafile
  isifile1 = isifile.replace('m****', 'memek')
  isifile2 = isifile1.replace('n******', 'ngentot')
  isifile3 = isifile2.replace('t**', 'tai')
  isifile4 = isifile3.replace('b******', 'bangsat')
  isifile5 = isifile4.replace('k*****', 'kontol')
  isifile6 = isifile5.replace('-', ' ')  
  return isifile6

def preprocessing(namafile):
  lowercase_sentence = namafile.lower()
  lowercase_sentence = re.sub(r"\d+", "",lowercase_sentence)
  lowercase_sentence = lowercase_sentence.translate(str.maketrans("","",string.punctuation))
  lowercase_sentence = lowercase_sentence.strip()
  factory = StemmerFactory()
  stemmer = factory.create_stemmer()
  hasil_stem = stemmer.stem(lowercase_sentence)
  tokens = nltk.tokenize.word_tokenize(lowercase_sentence)
  stop_factory = StopWordRemoverFactory()
  more_stopword = ['gitu', 'aja', 'bro', 'ku', 'lu', 'gimana', 'gua', 'kalo', 'kayak', 'tuh', 'gus', 'yaelah', 'si']
  data = stop_factory.get_stop_words()+more_stopword
  stopword = stop_factory.create_stop_word_remover()
  hasil_stopword = []
  print(tokens)
  for t in tokens:
    if t not in data:
      hasil_stopword.append(t)
  print(hasil_stopword)
  return hasil_stopword

def deteksi(namafile):
  database_kasar = ks.objects.all()
  kasarDB = []
  for i in database_kasar:
    kasarDB.append({'kata_kasar':i.kata_kasar, 'label':i.label})
  deteksi_kasar = []
  for j in namafile:
    for k in kasarDB:
      if j == k['kata_kasar']:
        deteksi_kasar.append(j)
  print(deteksi_kasar)
  if len(deteksi_kasar) != 0:
    return deteksi_kasar 
  else:
    hasil_deteksi = "Tidak terdeteksi kata kasar"
    return hasil_deteksi

def klasifikasi(namafile, hasilsw):
  print(namafile)
  database_kasar = ks.objects.all()
  kasarDB = []
  for i in database_kasar:
    kasarDB.append({'kata_kasar':i.kata_kasar, 'label':i.label})
  skor = 0
  for i in namafile:
      for j in kasarDB:
        if i == j['kata_kasar']:
          if j['label'] == "kasar1":
            skor = skor + 1
          elif j['label'] == "kasar2":
            skor = skor + 2
          elif j['label'] == "kasar3":
            skor = skor + len(hasilsw)
  print(skor)
  rating = ''
  batas = 0.5 * len(hasilsw)
  print(batas)
  if skor <= 0:
      rating = "A"
  elif skor <= batas and skor > 0:
      rating = "R"
  elif skor > batas:
      rating = "D"
  return rating

def youtube(namafile):
  video = YouTube(namafile)

  # setting video resolution
  stream = video.streams.get_lowest_resolution()
  
  namavideo = video.title
  split = namavideo.split()
  namanya= '_'.join(split)

  # downloads video
  stream.download('toxic/AudioFile/', filename = namanya+'.mp4')

  mp4_file = 'toxic/AudioFile/'+namanya+'.mp4'
  mp3_file = 'toxic/AudioFile/'+namanya+'.mp3'
  file_mp3 = namanya+'.mp3'

  videoClip = VideoFileClip(mp4_file)
  audioclip = videoClip.audio
  audioclip.write_audiofile(mp3_file)

  audioclip.close()
  videoClip.close()
  return file_mp3

def index(request):
  if request.method == 'POST':
    myfile = request.FILES['okey']
    handle_uploaded_file(myfile, myfile.name)
    konvert = konversi(myfile.name)
    data = transkrip(konvert)
    cetak = perbaikan(data)
    tekspp = preprocessing(cetak)
    hasil = deteksi(tekspp)
    final = klasifikasi(hasil, tekspp)
    sekarang = datetime.datetime.now()
    q = rp(link_yt='', nama_video=myfile.name, hasil_transkripsi=data, hasil_deteksi=hasil, klasifikasi=final, tanggal=sekarang)
    q.save()
    return render(request, 'index.html', {'cetak':cetak, 'hasil':hasil, "logg": hasil, "suara":myfile, 'final':final})
  else:
    return render(request, 'index.html')

def tampil(request):
  if request.method == 'POST':
    link = request.POST['link']
    video = youtube(link)
    konvert = konversi(video)
    data = transkrip(konvert)
    cetak = perbaikan(data)
    tekspp = preprocessing(cetak)
    hasil = deteksi(tekspp)
    final = klasifikasi(hasil, tekspp)
    sekarang = datetime.datetime.now()
    q = rp(link_yt=link, nama_video=video, hasil_transkripsi=data, hasil_deteksi=hasil, klasifikasi=final, tanggal=sekarang)
    q.save()
    return render(request, 'tampil.html', {'cetak':cetak, 'hasil':hasil, "logg": hasil, "suara":video, 'final':final})
  return render(request, 'tampil.html')

def kamus(request):
  isi = ks.objects.all()
  isi_saran = srn.objects.all()
  if request.method == 'POST':
    saran_kata = request.POST.get('nama')
    label = request.POST.get('labels')
    q = srn(saran_kata=saran_kata, label=label)
    q.save()
  kasar1 = []
  kasar2 = []
  kasar3 = []
  for i in isi:
    if i.label == "kasar1":
      kasar1.append({'kata_kasar':i.kata_kasar, 'label':i.label})
    elif i.label == "kasar2":
      kasar2.append({'kata_kasar':i.kata_kasar, 'label':i.label})
    elif i.label == "kasar3":
      kasar3.append({'kata_kasar':i.kata_kasar, 'label':i.label})
  return render(request, 'kamus.html', {'isi':isi, 'isi_saran':isi_saran, 'satu':kasar1, 'dua':kasar2, 'tiga':kasar3})

def rekaps(request):
  isi = rp.objects.all()
  return render(request, 'rekaps.html', {'isi':isi})