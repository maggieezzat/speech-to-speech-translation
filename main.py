from flask import Flask
import requests as rq
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask_session import Session
from config import Config
import os
import uuid
import time
import json
import sys
import re
sys.path.append('/usr/bin/ffmpeg')
from pydub import AudioSegment
AudioSegment.converter = "/usr/bin/ffmpeg"
AudioSegment.ffmpeg = "/usr/bin/ffmpeg"
AudioSegment.ffprobe ="/usr/bin/ffprobe"


app = Flask(__name__)
app.secret_key = os.urandom(24)

def complete_tashkeel(sentence):

    new_sentence = sentence
    for m in re.finditer('[\u0621-\u064A]\u0627', sentence):
        #or m.group(0)[0] =='\u064A'
        if m.group(0)[0] == '\u0627'  or m.group(0)[0] == '\u0648' or m.group(0)[0] == '\u0625':
          continue
        new_sentence = new_sentence.replace(m.group(0), m.group(0)[0]+'َ'+m.group(0)[1])

    sentence = new_sentence
    newer_sentence = sentence

    for m in re.finditer('[\u0621-\u064A]\u064A', sentence):
        if m.group(0)[0] == '\u0627' or m.group(0)[0] =='\u064A' or m.group(0)[0] == '\u0648' or m.group(0)[0] == '\u0623':
          continue 
        newer_sentence = newer_sentence.replace(m.group(0), m.group(0)[0]+'ِ'+m.group(0)[1])

    sentence = newer_sentence
    final_sentence = sentence

    for m in re.finditer('[\u0621-\u064A]\u0648', sentence):
        if m.group(0)[0] == '\u0627' or m.group(0)[0] =='\u064A' or m.group(0)[0] == '\u0648' or m.group(0)[0] =='\u0625':
          continue 
        newer_sentence = newer_sentence.replace(m.group(0), m.group(0)[0]+'ُ'+m.group(0)[1])

    sentence = newer_sentence
    final_sentence = sentence

    for m in re.finditer('[\u0621-\u064A]\u0651\u0627', sentence):
        newer_sentence = newer_sentence.replace(m.group(0), m.group(0)[0]+'َّ'+m.group(0)[2])

    sentence = newer_sentence
    final_sentence = sentence

    for m in re.finditer('[\u0621-\u064A]\u0651\u064A', sentence):
        newer_sentence = newer_sentence.replace(m.group(0), m.group(0)[0]+'ِّ'+m.group(0)[2])
    sentence = newer_sentence
    final_sentence = sentence

    for m in re.finditer('[\u0621-\u064A]\u0651\u0648', sentence):
        final_sentence = newer_sentence.replace(m.group(0), m.group(0)[0]+'ُّ'+m.group(0)[2])  

    return final_sentence

"""
@app.route("/")
def welcome():

    if 'in_file' in session.keys():
        if session['do_trans'] == 'true':
            return render_template('record.html', 
                in_file = session['in_file'], 
                asr_out = session['asr_out'],
                trans_ch = session['trans_ch'],
                trans_en = session['trans_en'],
                trans_fr = session['trans_fr'],
                trans_ch_ar = session['trans_ch_ar'],
                trans_en_ar = session['trans_en_ar'],
                trans_fr_ar = session['trans_fr_ar'],
                diac_sent=session['diac_sent'],
                out_female_file = session['out_female_file'],
                out_male_file = session['out_male_file'])
        else:
            #print("I AM HERE")
            return render_template('record.html', 
                in_file = session['in_file'], 
                asr_out = session['asr_out'],
                diac_sent=session['diac_sent'],
                out_female_file = session['out_female_file'],
                out_male_file = session['out_male_file'])

    
    elif 'error_message' in session.keys():
        print('error message exists')
        return render_template("record.html", error_message=session['error_message'])

    else:
        print("NO INPUT FILE")
        return render_template("record.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload():

    #do_trans = request.args.get('trans')
    do_trans = 'true'
    ######################################
    session['do_trans'] = do_trans

    filename = 'input_file.wav'
    audio_data = request.data

    output_dir = str(int(time.time()))

    os.makedirs(output_dir)
    os.makedirs(os.path.join(output_dir, 'ASR'))
    
    session['in_file'] = filename

    save_dir = 'static'

    ###################################### 1. SPEECH RECOGNITION ######################################
    try:
        start = time.time()
        
        with open(os.path.join(save_dir, filename), 'wb') as f:
            f.write(audio_data)

        with open(os.path.join(output_dir, 'ASR', filename), 'wb') as f:
            f.write(audio_data)
        
        end = time.time()
        prep_time = end - start
        print("PREP Time: " + str(prep_time))
        
        start = time.time()
        url = 'http://espnetdecoding.eastus.cloudapp.azure.com:6000'
        #url ='bla bla blo'
        files = {'file': open(os.path.join(save_dir, filename), 'rb')}

        r = rq.post(url, files=files)
        asr_out = json.loads(r.text)['transcript']

        with open(os.path.join(output_dir, 'ASR', 'asr_output.txt'), 'w') as f:
            f.write(asr_out + '\n')
        
        #asr_out='مرحبا فى مركز الابتكار'
        
        session['asr_out'] = asr_out.replace('<صخث>', '***')

        end = time.time()
        asr_time = end - start
        
        print("ASR Time: " + str(asr_time))
    except:
        print("ERROR FETCHING ASR OUTPUT")
        
        session.pop('in_file', None)
        session.pop('asr_out', None)
        session.pop('trans_ch', None)
        session.pop('trans_en', None)
        session.pop('trans_fr', None)
        session.pop('trans_ch_ar', None)
        session.pop('trans_en_ar', None)
        session.pop('trans_fr_ar', None)
        session.pop('diac_sent', None)
        session.pop('out_female_file', None)
        session.pop('out_male_file', None)
        

        session['error_message'] = 'There has been a problem with the ASR output.'
        #print(session['error_message'])
        return render_template("record.html", error_message=session['error_message'])
        #session.pop('error_message', None)
        #return render_template("record.html")
    
    if do_trans == 'true':
        ###################################### 2. CHINESE/ENGLISH/FRENCH TRANSLATION ######################################
        try:
            os.makedirs(os.path.join(output_dir, 'MT'))

            #CHINESE
            url = 'http://52.168.2.102:5000/translate'
            payload = {"text": asr_out.replace('<صخث>', ''), "source":"ar", "target":"zh"}
            file_response = rq.post(url, headers = {'content-type': "application/json"}, json=payload)
            trans_ch = file_response.json()['output']
            session['trans_ch'] = trans_ch

            with open(os.path.join(output_dir, 'MT', 'trans_chinese.txt'), 'w') as f:
                f.write(trans_ch + '\n')
            
            
            #ENGLISH
            url = 'http://52.168.2.102:5000/translate'
            payload = {"text": asr_out.replace('<صخث>', ''), "source":"ar", "target":"en"}
            file_response = rq.post(url, headers = {'content-type': "application/json"}, json=payload)
            trans_en = file_response.json()['output']
            #trans_en = 'Hi! This feature is under construction.'
            session['trans_en'] = trans_en

            with open(os.path.join(output_dir, 'MT', 'trans_english.txt'), 'w') as f:
                f.write(trans_en + '\n')
            
            #FRENCH
            url = 'http://52.168.2.102:5000/translate'
            payload = {"text": asr_out.replace('<صخث>', ''), "source":"ar", "target":"fr"}
            file_response = rq.post(url, headers = {'content-type': "application/json"}, json=payload)
            trans_fr = file_response.json()['output']
            #trans_fr = " Hi! Cette fonctionnalité en sous construction."
            session['trans_fr'] = trans_fr

            with open(os.path.join(output_dir, 'MT', 'trans_french.txt'), 'w') as f:
                f.write(trans_fr + '\n')

            ###################################### 3. ARABIC TRANSLATION ######################################
            #CH/AR
            url = 'http://52.168.2.102:5000/translate'
            payload = {"text": trans_ch, "source":"zh", "target":"ar"}
            file_response = rq.post(url, headers = {'content-type': "application/json"}, json=payload)
            trans_ch_ar = file_response.json()['output']
            session['trans_ch_ar'] = trans_ch_ar

            with open(os.path.join(output_dir, 'MT', 'trans_ch_arabic.txt'), 'w') as f:
                f.write(trans_ch_ar + '\n')
            
            #EN/AR
            url = 'http://52.168.2.102:5000/translate'
            payload = {"text": trans_en, "source":"en", "target":"ar"}
            file_response = rq.post(url, headers = {'content-type': "application/json"}, json=payload)
            trans_en_ar = file_response.json()['output']
            #trans_en_ar = 'مرحبا! هذه الخاصية تحت الانشاء'
            session['trans_en_ar'] = trans_en_ar

            with open(os.path.join(output_dir, 'MT', 'trans_en_arabic.txt'), 'w') as f:
                f.write(trans_en_ar + '\n')

            #FR/AR
            url = 'http://52.168.2.102:5000/translate'
            payload = {"text": trans_fr, "source":"fr", "target":"ar"}
            file_response = rq.post(url, headers = {'content-type': "application/json"}, json=payload)
            trans_fr_ar = file_response.json()['output']
            #trans_fr_ar = 'مرحبا! هذه الخاصية تحت الانشاء'
            session['trans_fr_ar'] = trans_fr_ar

            with open(os.path.join(output_dir, 'MT', 'trans_fr_arabic.txt'), 'w') as f:
                f.write(trans_fr_ar + '\n')

        except:
            print("ERROR FETCHING MT OUTPUT")
            session.pop('in_file', None)
            session.pop('asr_out', None)
            session.pop('trans_ch', None)
            session.pop('trans_en', None)
            session.pop('trans_fr', None)
            session.pop('trans_ch_ar', None)
            session.pop('trans_en_ar', None)
            session.pop('trans_fr_ar', None)
            session.pop('diac_sent', None)
            session.pop('out_female_file', None)
            session.pop('out_male_file', None)
            session['error_message'] = 'There has been a problem with the translation. Please retry.'
            return render_template("record.html",error_message= session['error_message'])
    else:
        trans_en_ar = asr_out

    ###################################### 4. DIACTRIZATION ######################################
    try:
        start = time.time()
        trans_en_ar = trans_en_ar.replace('.', ' ')
        trans_en_ar = trans_en_ar.replace(',', ' ')
        trans_en_ar = trans_en_ar.replace('?', ' ')
        trans_en_ar = trans_en_ar.replace('؟', ' ')
        trans_en_ar = trans_en_ar.replace('!', ' ')
        trans_en_ar = trans_en_ar.replace('\\', ' ')
        trans_en_ar = trans_en_ar.replace('/', ' ')
        trans_en_ar = trans_en_ar.replace('،', ' ')
        trans_en_ar = re.sub(r'\d+', ' ', trans_en_ar)
        trans_en_ar = re.sub(' +', ' ', trans_en_ar)
        payload = {'text': trans_en_ar}
        #payload = {'text': asr_out}
        req = rq.post('https://farasa-api.qcri.org/msa/webapi/diacritizeV2', headers = {'content-type': "application/json"}, json=payload)
        diac_sent = req.json()['output']
        diac_sent = complete_tashkeel(diac_sent)
        session['diac_sent'] = diac_sent

        os.makedirs(os.path.join(output_dir, 'TTS'))

        with open(os.path.join(output_dir, 'TTS', 'diacritized_sent.txt'), 'w') as f:
                f.write(diac_sent + '\n')

        end = time.time()
        diac_time = end - start
        print("DIAC Time: " + str(diac_time))
    except:
        print("ERROR FETCHING DIAC OUTPUT")
        session.pop('in_file', None)
        session.pop('asr_out', None)
        session.pop('trans_ch', None)
        session.pop('trans_en', None)
        session.pop('trans_fr', None)
        session.pop('trans_ch_ar', None)
        session.pop('trans_en_ar', None)
        session.pop('trans_fr_ar', None)
        session.pop('diac_sent', None)
        session.pop('out_female_file', None)
        session.pop('out_male_file', None)
        session['error_message'] = 'There has been a problem with the diacritization. Please retry.'
        return render_template("record.html", error_message = session['error_message'] )

    ###################################### 5. TEXT TO SPEECH ######################################
    try:
        start = time.time()
        url = 'http://40.91.64.226:5000/'
        diac_sent = 'ي ' + diac_sent
        params = {'txt' : diac_sent, 'gender' : '0'}
        file_response = rq.post(url, params=params)

        out_male = 'out_male_{}.wav'.format(str(int(time.time())))
        out_female = 'out_female_{}.wav'.format(str(int(time.time())))

        if os.path.exists(os.path.join(save_dir, out_female)):
            os.remove(os.path.join(save_dir, out_female))
        with open(os.path.join(save_dir, out_female), 'wb') as f:
            f.write(file_response.content)
        with open(os.path.join(output_dir, 'TTS', 'out_female.wav'), 'wb') as f:
            f.write(file_response.content)
        
        session['out_female_file'] = out_female

        url = 'http://40.91.64.226:5000/'
        params = {'txt' : diac_sent, 'gender' : '1'}
        file_response = rq.post(url, params=params)
        if os.path.exists(os.path.join(save_dir, out_male)):
            os.remove(os.path.join(save_dir, out_male))
        with open(os.path.join(save_dir, out_male), 'wb') as f:
            f.write(file_response.content)
        with open(os.path.join(output_dir, 'TTS', 'out_male.wav'), 'wb') as f:
            f.write(file_response.content)
        
        session['out_male_file'] = out_male
        
        end = time.time()
        tts_time = end - start
        print("TTS Time: " + str(tts_time))
    except:
        print("ERROR FETCHING TTS OUTPUT")
        session.pop('in_file', None)
        session.pop('asr_out', None)
        session.pop('trans_ch', None)
        session.pop('trans_en', None)
        session.pop('trans_fr', None)
        session.pop('trans_ch_ar', None)
        session.pop('trans_en_ar', None)
        session.pop('trans_fr_ar', None)
        session.pop('diac_sent', None)
        session.pop('out_female_file', None)
        session.pop('out_male_file', None)
        session['error_message'] = 'There has been a problem with converting the text to speech. Please retry'
        return render_template("record.html", error_message=session['error_message'])
        
    print("Successfully Excuted the Pipeline")
    
    if do_trans == 'true':
        return render_template('record.html', 
            in_file = session['in_file'], 
            asr_out = session['asr_out'],
            trans_ch = session['trans_ch'],
            trans_en = session['trans_en'],
            trans_fr = session['trans_fr'],
            trans_en_ar = session['trans_en_ar'],
            trans_fr_ar = session['trans_fr_ar'],
            diac_sent = session['diac_sent'],
            out_female_file = session['out_female_file'],
            out_male_file = session['out_male_file'])
    else:
        #print(session['in_file'])
        #print(session['asr_out'])
        #print(session['diac_sent'])
        #print(session['out_female_file'])
        #print(session['out_male_file'])
        return render_template('record.html', 
            in_file = session['in_file'], 
            asr_out = session['asr_out'],
            diac_sent = session['diac_sent'],
            out_female_file = session['out_female_file'],
            out_male_file = session['out_male_file'])
"""
@app.route("/")
def welcome():

    if 'in_file' in session.keys():
       return render_template('record.html', 
                in_file = session['in_file'], 
                asr_out = session['asr_out'])

    
    elif 'error_message' in session.keys():
        print('error message exists')
        return render_template("record.html", error_message=session['error_message'])

    else:
        print("NO INPUT FILE")
        return render_template("record.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload():

    filename = 'input_file.wav'
    audio_data = request.data

    output_dir = str(int(time.time()))

    os.makedirs(output_dir)
    os.makedirs(os.path.join(output_dir, 'ASR'))
    
    session['in_file'] = filename

    save_dir = 'static'

    ###################################### 1. SPEECH RECOGNITION ######################################
    try:
        start = time.time()
        
        with open(os.path.join(save_dir, filename), 'wb') as f:
            f.write(audio_data)

        with open(os.path.join(output_dir, 'ASR', filename), 'wb') as f:
            f.write(audio_data)
        
        end = time.time()
        prep_time = end - start
        print("PREP Time: " + str(prep_time))
        
        start = time.time()
        url = 'http://41.179.247.131/:6000'
        files = {'file': open(os.path.join(save_dir, filename), 'rb')}

        r = rq.post(url, files=files)
        asr_out = json.loads(r.text)['transcript']
        #asr_out='مرحبا فى مركز الابتكار'

        with open(os.path.join(output_dir, 'ASR', 'asr_output.txt'), 'w') as f:
            f.write(asr_out + '\n')
        
        session['asr_out'] = asr_out.replace('<صخث>', '***')

        end = time.time()
        asr_time = end - start
        
        print("ASR Time: " + str(asr_time))
        
        return render_template('record.html', 
            in_file = session['in_file'], 
            asr_out = session['asr_out'])
    except:
        print("ERROR FETCHING ASR OUTPUT")
        
        session.pop('in_file', None)
        session.pop('asr_out', None)
        
        session['error_message'] = 'There has been a problem with the ASR output.'
        return render_template("record.html", error_message=session['error_message'])


if __name__ == "__main__":
    #app.secret_key = os.urandom(24)
    app.config.from_object(Config)
    Session(app)
    app.run()
