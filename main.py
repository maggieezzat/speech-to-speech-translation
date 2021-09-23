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
from Languages import get_lang_ASR, get_lang_MT, get_lang_TTS, get_lang_Speaker
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


@app.route("/record")
def welcome():
    if 'in_file' in session.keys():
        return render_template('record.html',
            in_file = session['in_file'], 
            asr_out = session['asr_out'],
            trans_out = session['trans_out'],
            diac_sent=session['diac_sent'],
            out_female_file = session['out_female_file'],
            out_male_file = session['out_male_file'])

    
    elif 'error_message' in session.keys():
        print('error message exists')
        return render_template("record.html", error_message=session['error_message'])

    else:
        print("NO INPUT FILE")
        return render_template("record.html")

@app.route('/')
def selectLanguage_page():
    target = [['source language'], ['destination language']] 
    language = [['English'], ['French'], ['Chinese'], ['Russian'], ['Ukraninan']]

    return render_template("ChooseLanguage.html", lang=language, target=target)

@app.route("/asr_egy_v2")
def asr_egy_v2():

    if 'in_file_egy_v2' in session.keys():
        return render_template('egy_v2.html', 
            in_file_asr_only = session['in_file_egy_v2'], 
            out_file_asr_only = session['out_file_egy_v2'])
    elif 'error_message' in session.keys():
        print('error message exists')
        return render_template("egy_v2.html", error_message=session['error_message'])
    else:
        print("NO INPUT FILE")
        return render_template("egy_v2.html")



@app.route("/asr_egy_v2_finetuned")
def asr_egy_v2_finetuned():

    if 'in_file_egy_v2_finetuned' in session.keys():
        return render_template('egy_v2_finetuned.html', 
            in_file_asr_only = session['in_file_egy_v2_finetuned'], 
            out_file_asr_only = session['out_file_egy_v2_finetuned'])
    elif 'error_message' in session.keys():
        print('error message exists')
        return render_template("egy_v2_finetuned.html", error_message=session['error_message'])
    else:
        print("NO INPUT FILE")
        return render_template("egy_v2_finetuned.html")



@app.route("/asr_conformer_large")
def asr_conformer_large():

    if 'in_file_conformer_large' in session.keys():
        return render_template('conformer_large.html', 
            in_file_asr_only = session['in_file_conformer_large'], 
            out_file_asr_only = session['out_file_conformer_large'])
    elif 'error_message' in session.keys():
        print('error message exists')
        return render_template("conformer_large.html", error_message=session['error_message'])
    else:
        print("NO INPUT FILE")
        return render_template("conformer_large.html")



@app.route("/asr_conformer_large_finetuned")
def asr_conformer_large_finetuned():

    if 'in_file_conformer_large_finetuned' in session.keys():
        return render_template('conformer_large_finetuned.html', 
            in_file_asr_only = session['in_file_conformer_large_finetuned'], 
            out_file_asr_only = session['out_file_conformer_large_finetuned'])
    elif 'error_message' in session.keys():
        print('error message exists')
        return render_template("conformer_large_finetuned.html", error_message=session['error_message'])
    else:
        print("NO INPUT FILE")
        return render_template("conformer_large_finetuned.html")




@app.route('/upload', methods=['GET', 'POST'])
def upload():

    src_lang = request.args.get('src_lang')
    dest_lang = request.args.get('dest_lang')
    ######################################

    filename = 'input_file.webm'
    audio_data = request.data

    save_dir = 'static'
    output_dir = str(int(time.time()))

    os.makedirs(os.path.join(save_dir, output_dir, 'ASR'))
       
    ###################################### 1. SPEECH RECOGNITION ######################################
    try:
        start = time.time()

        with open(os.path.join(save_dir, output_dir, 'ASR', filename), 'wb') as f:
            f.write(audio_data)

        session['in_file'] = os.path.join(output_dir, 'ASR', filename)
        
        end = time.time()
        prep_time = end - start
        print("PREP Time: " + str(prep_time))
        
        start = time.time()
        if (src_lang == 'Arabic'):
            url = 'http://41.179.247.131:6002/'
        else:
            lang_code = get_lang_ASR(src_lang)
            url = 'http://41.179.247.131:6090?sampling_rate=8000&language_code='+lang_code
        files = {'file': open(os.path.join(save_dir,  output_dir, 'ASR', filename), 'rb')}

        r = rq.post(url, files=files)
        asr_out = json.loads(r.text)['transcript']

        with open(os.path.join(save_dir, output_dir, 'ASR', 'asr_output.txt'), 'w') as f:
            f.write(asr_out + '\n')
        
        asr_out = asr_out.replace('<صخث>', '***')
        asr_out = asr_out.replace('<noise>', '***')
        session['asr_out'] = asr_out

        end = time.time()
        asr_time = end - start
        
        print("ASR Time: " + str(asr_time))
    except Exception as e: 
        print(e)
        print("ERROR FETCHING ASR OUTPUT")
        session.pop('in_file', None)
        session.pop('asr_out', None)
        session.pop('trans_out', None)
        session.pop('diac_sent', None)
        session.pop('out_female_file', None)
        session.pop('out_male_file', None)
        session['error_message'] = 'There has been a problem with the ASR output.'
        return render_template("record.html", error_message=session['error_message'])
    
        ###################################### TRANSLATION ######################################
    try:
        os.makedirs(os.path.join(save_dir, output_dir, 'MT'))

        #translation
        url = 'http://41.179.247.131:9704/translate'
        payload = {"text": asr_out.replace('<صخث>', ''), "source":get_lang_MT(src_lang), "target":get_lang_MT(dest_lang)}
        file_response = rq.post(url, headers = {'Content-Type': "application/json"}, json=payload)
        trans_out = file_response.json()['output']
        session['trans_out'] = trans_out

        with open(os.path.join(save_dir, output_dir, 'MT', 'trans_out.txt'), 'w') as f:
            f.write(trans_out + '\n')
        
    except Exception as e: 
        print(e)
        print("ERROR FETCHING MT OUTPUT")
        session.pop('in_file', None)
        session.pop('asr_out', None)
        session.pop('trans_out', None)
        session.pop('diac_sent', None)
        session.pop('out_female_file', None)
        session.pop('out_male_file', None)
        session['error_message'] = 'There has been a problem with the translation. Please retry.'
        return render_template("record.html",error_message= session['error_message'])


    ###################################### 4. DIACTRIZATION ######################################
    os.makedirs(os.path.join(save_dir, output_dir, 'TTS'))

    if dest_lang == "Arabic":
        try:
            start = time.time()
            trans_out = trans_out.replace('.', ' ')
            trans_out = trans_out.replace(',', ' ')
            trans_out = trans_out.replace('?', ' ')
            trans_out = trans_out.replace('؟', ' ')
            trans_out = trans_out.replace('!', ' ')
            trans_out = trans_out.replace('\\', ' ')
            trans_out = trans_out.replace('/', ' ')
            trans_out = trans_out.replace('،', ' ')
            trans_out = re.sub(r'\d+', ' ', trans_out)
            trans_out = re.sub(' +', ' ', trans_out)
            payload = {'text': trans_out}
            req = rq.post('https://farasa-api.qcri.org/msa/webapi/diacritizeV2', headers = {'content-type': "application/json"}, json=payload)
            diac_sent = req.json()['output']
            diac_sent = complete_tashkeel(diac_sent)
            session['diac_sent'] = diac_sent

            # os.makedirs(os.path.join(save_dir, output_dir, 'TTS'))

            with open(os.path.join(save_dir, output_dir, 'TTS', 'diacritized_sent.txt'), 'w') as f:
                    f.write(diac_sent + '\n')
            
            end = time.time()
            diac_time = end - start
            print("DIAC Time: " + str(diac_time))
        except Exception as e: 
            print(e)
            print("ERROR FETCHING DIAC OUTPUT")
            session.pop('in_file', None)
            session.pop('asr_out', None)
            session.pop('trans_out', None)
            session.pop('diac_sent', None)
            session.pop('out_female_file', None)
            session.pop('out_male_file', None)
            session['error_message'] = 'There has been a problem with the diacritization. Please retry.'
            return render_template("record.html", error_message = session['error_message'] )
    else:
        session['diac_sent'] = None
    ###################################### 5. TEXT TO SPEECH ######################################
    try:
        start = time.time()
        if dest_lang == "Arabic":
            url = 'http://41.179.247.131:5000/'
            diac_sent = 'ي ' + diac_sent
            params = {'txt' : diac_sent, 'gender' : '0'}

            file_response = rq.post(url, params=params)
            out_male = 'out_male_{}.mp3'.format(str(int(time.time())))
            out_female = 'out_female_{}.mp3'.format(str(int(time.time())))

            with open(os.path.join(save_dir, output_dir, 'TTS', out_female), 'wb') as f:
                f.write(file_response.content)
            
            session['out_female_file'] = os.path.join( output_dir, 'TTS', out_female)

            url = 'http://41.179.247.131:5000/'
            params = {'txt' : diac_sent, 'gender' : '1'}
            file_response = rq.post(url, params=params)

            with open(os.path.join(save_dir, output_dir, 'TTS', out_male), 'wb') as f:
                f.write(file_response.content)
            
            session['out_male_file'] = os.path.join( output_dir, 'TTS', out_male)
        else:
            out_male = 'out_male_{}.mp3'.format(str(int(time.time())))
            out_female = 'out_female_{}.mp3'.format(str(int(time.time())))
            url = 'http://41.179.247.131:6091/'
            speaker = get_lang_Speaker(dest_lang)
            language = get_lang_TTS(dest_lang)

            if "m" in speaker.keys():
                male_params = '?text='+trans_out+'&speaker='+speaker["m"]+'&language_code='+language+'&sampling_rate=8000'
                file_response = rq.post(url+male_params)
                with open(os.path.join(save_dir, output_dir, 'TTS', out_male), 'wb') as f:
                    f.write(file_response.content)
                session['out_male_file'] = os.path.join( output_dir, 'TTS', out_male)

            if "f" in speaker.keys():
                female_params = '?text='+trans_out+'&speaker='+speaker["f"]+'&language_code='+language+'&sampling_rate=8000'
                file_response = rq.post(url+female_params)
                with open(os.path.join(save_dir, output_dir, 'TTS', out_female), 'wb') as f:
                    f.write(file_response.content)
                session['out_female_file'] = os.path.join( output_dir, 'TTS', out_female)

        end = time.time()
        tts_time = end - start
        print("TTS Time: " + str(tts_time))
    except Exception as e: 
        print(e)
        print("ERROR FETCHING TTS OUTPUT")
        session.pop('in_file', None)
        session.pop('asr_out', None)
        session.pop('trans_out', None)
        session.pop('diac_sent', None)
        session.pop('out_female_file', None)
        session.pop('out_male_file', None)
        session['error_message'] = 'There has been a problem with converting the text to speech. Please retry'
        return render_template("record.html", error_message=session['error_message'])
        
    print("Successfully Excuted the Pipeline")
    return render_template('record.html', 
    in_file = session['in_file'], 
    asr_out = session['asr_out'],
    trans_out = session['trans_out'],
    diac_sent = session['diac_sent'],
    out_female_file = session['out_female_file'],
    out_male_file = session['out_male_file'])



@app.route('/uploadEgyV2', methods=['GET', 'POST'])
def uploadEgyV2():

    ######################################

    filename = 'input_file.webm'
    audio_data = request.data

    save_dir = 'static'
    output_dir = str(int(time.time()))

    os.makedirs(os.path.join(save_dir, output_dir, 'ASR'))

    ###################################### 1. SPEECH RECOGNITION ######################################
    try:
        start = time.time()

        with open(os.path.join(save_dir, output_dir, 'ASR', filename), 'wb') as f:
            f.write(audio_data)

        session['in_file_egy_v2'] = os.path.join( output_dir, 'ASR', filename)
        
        end = time.time()
        prep_time = end - start
        print("PREP Time: " + str(prep_time))
        
        start = time.time()
        url = 'http://41.179.247.131:6000/'
        files = {'file': open(os.path.join(save_dir, output_dir, 'ASR', filename), 'rb')}

        r = rq.post(url, files=files)
        asr_out = json.loads(r.text)['transcript']

        with open(os.path.join(save_dir, output_dir, 'ASR', 'asr_output.txt'), 'w') as f:
            f.write(asr_out + '\n')
        
        session['out_file_egy_v2'] = asr_out.replace('<صخث>', '***')

        end = time.time()
        asr_time = end - start
        
        print("ASR Time: " + str(asr_time))
    except Exception as e: 
        print(e)
        print("ERROR FETCHING ASR OUTPUT")
        
        session.pop('in_file_egy_v2', None)
        session.pop('out_file_egy_v2', None)
        session['error_message'] = 'There has been a problem with the ASR output.'
        return render_template("egy_v2.html", error_message=session['error_message'])
        
    print("Successfully Excuted the Pipeline")
    
    return render_template('egy_v2.html', 
        in_file_asr_only = session['in_file_egy_v2'], 
        out_file_asr_only = session['out_file_egy_v2'])



@app.route('/uploadEgyV2Finetuned', methods=['GET', 'POST'])
def uploadEgyV2Finetuned():

    ######################################

    filename = 'input_file.webm'
    audio_data = request.data

    save_dir = 'static'
    output_dir = str(int(time.time()))

    os.makedirs(os.path.join(save_dir, output_dir, 'ASR'))

    ###################################### 1. SPEECH RECOGNITION ######################################
    try:
        start = time.time()

        with open(os.path.join(save_dir, output_dir, 'ASR', filename), 'wb') as f:
            f.write(audio_data)

        session['in_file_egy_v2_finetuned'] = os.path.join( output_dir, 'ASR', filename)
        
        end = time.time()
        prep_time = end - start
        print("PREP Time: " + str(prep_time))
        
        start = time.time()
        url = 'http://41.179.247.131:6001/'
        files = {'file': open(os.path.join(save_dir, output_dir, 'ASR', filename), 'rb')}

        r = rq.post(url, files=files)
        asr_out = json.loads(r.text)['transcript']

        with open(os.path.join(save_dir, output_dir, 'ASR', 'asr_output.txt'), 'w') as f:
            f.write(asr_out + '\n')
        
        session['out_file_egy_v2_finetuned'] = asr_out.replace('<صخث>', '***')

        end = time.time()
        asr_time = end - start
        
        print("ASR Time: " + str(asr_time))
    except Exception as e: 
        print(e)
        print("ERROR FETCHING ASR OUTPUT")
        
        session.pop('in_file_egy_v2_finetuned', None)
        session.pop('out_file_egy_v2_finetuned', None)
        session['error_message'] = 'There has been a problem with the ASR output.'
        return render_template("egy_v2_finetuned.html", error_message=session['error_message'])
        
    print("Successfully Excuted the Pipeline")
    
    return render_template('egy_v2_finetuned.html', 
        in_file_asr_only = session['in_file_egy_v2_finetuned'], 
        out_file_asr_only = session['out_file_egy_v2_finetuned'])




@app.route('/uploadConformerLarge', methods=['GET', 'POST'])
def uploadConformerLarge():

    ######################################

    filename = 'input_file.webm'
    audio_data = request.data

    save_dir = 'static'
    output_dir = str(int(time.time()))

    os.makedirs(os.path.join(save_dir, output_dir, 'ASR'))

    ###################################### 1. SPEECH RECOGNITION ######################################
    try:
        start = time.time()

        with open(os.path.join(save_dir, output_dir, 'ASR', filename), 'wb') as f:
            f.write(audio_data)

        session['in_file_conformer_large'] = os.path.join( output_dir, 'ASR', filename)
        
        end = time.time()
        prep_time = end - start
        print("PREP Time: " + str(prep_time))
        
        start = time.time()
        url = 'http://41.179.247.131:6002/'
        files = {'file': open(os.path.join(save_dir, output_dir, 'ASR', filename), 'rb')}

        r = rq.post(url, files=files)
        asr_out = json.loads(r.text)['transcript']

        with open(os.path.join(save_dir, output_dir, 'ASR', 'asr_output.txt'), 'w') as f:
            f.write(asr_out + '\n')
        
        session['out_file_conformer_large'] = asr_out.replace('<صخث>', '***')

        end = time.time()
        asr_time = end - start
        
        print("ASR Time: " + str(asr_time))
    except Exception as e: 
        print(e)
        print("ERROR FETCHING ASR OUTPUT")
        
        session.pop('in_file_conformer_large', None)
        session.pop('out_file_conformer_large', None)
        session['error_message'] = 'There has been a problem with the ASR output.'
        return render_template("conformer_large.html", error_message=session['error_message'])
        
    print("Successfully Excuted the Pipeline")
    
    return render_template('conformer_large.html', 
        in_file_asr_only = session['in_file_conformer_large'], 
        out_file_asr_only = session['out_file_conformer_large'])



@app.route('/uploadConformerLargeFinetuned', methods=['GET', 'POST'])
def uploadConformerLargeFinetuned():

    ######################################

    filename = 'input_file.webm'
    audio_data = request.data

    save_dir = 'static'
    output_dir = str(int(time.time()))

    os.makedirs(os.path.join(save_dir, output_dir, 'ASR'))

    ###################################### 1. SPEECH RECOGNITION ######################################
    try:
        start = time.time()

        with open(os.path.join(save_dir, output_dir, 'ASR', filename), 'wb') as f:
            f.write(audio_data)

        session['in_file_conformer_large_finetuned'] = os.path.join( output_dir, 'ASR', filename)
        
        end = time.time()
        prep_time = end - start
        print("PREP Time: " + str(prep_time))
        
        start = time.time()
        url = 'http://41.179.247.131:6003/'
        files = {'file': open(os.path.join(save_dir, output_dir, 'ASR', filename), 'rb')}

        r = rq.post(url, files=files)
        asr_out = json.loads(r.text)['transcript']

        with open(os.path.join(save_dir, output_dir, 'ASR', 'asr_output.txt'), 'w') as f:
            f.write(asr_out + '\n')
        
        session['out_file_conformer_large_finetuned'] = asr_out.replace('<صخث>', '***')

        end = time.time()
        asr_time = end - start
        
        print("ASR Time: " + str(asr_time))
    except Exception as e: 
        print(e)
        print("ERROR FETCHING ASR OUTPUT")
        
        session.pop('in_file_conformer_large_finetuned', None)
        session.pop('out_file_conformer_large_finetuned', None)
        session['error_message'] = 'There has been a problem with the ASR output.'
        return render_template("conformer_large_finetuned.html", error_message=session['error_message'])
        
    print("Successfully Excuted the Pipeline")
    
    return render_template('conformer_large_finetuned.html', 
        in_file_asr_only = session['in_file_conformer_large_finetuned'], 
        out_file_asr_only = session['out_file_conformer_large_finetuned'])




if __name__ == "__main__":
    #app.secret_key = os.urandom(24)
    app.config.from_object(Config)
    Session(app)
    app.run()
