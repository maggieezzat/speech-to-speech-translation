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


@app.route("/")
def welcome():

    if 'in_file' in session.keys():
            return render_template('record.html', 
                in_file = session['in_file'], 
                asr_out = session['asr_out'],
                target_translation = session['target_translation'],
                diac_sent = session['diac_sent'],
                out_male_file = session['out_male_file'])

    elif 'error_message' in session.keys():
        print('error message exists')
        return render_template("record.html", error_message=session['error_message'])

    else:
        print("NO INPUT FILE")
        return render_template("record.html")



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

    #do_trans = request.args.get('trans')
    do_trans = 'true'
    ######################################
    session['do_trans'] = do_trans

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
        url = 'http://41.179.247.131:6002/'
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
    except:
        print("ERROR FETCHING ASR OUTPUT")
        
        session.pop('in_file', None)
        session.pop('asr_out', None)
        session.pop('target_translation', None)
        session.pop('diac_sent', None)
        session.pop('out_male_file', None)
        session['error_message'] = 'There has been a problem with the ASR output.'
        return render_template("record.html", error_message=session['error_message'])
    
    if do_trans == 'true':
        ###################################### 2. CHINESE/ENGLISH/FRENCH TRANSLATION ######################################
        try:
            os.makedirs(os.path.join(save_dir, output_dir, 'MT'))
            #target_translation
            src = "ar"
            target = "en"
            url = 'http://41.179.247.131:9704/translate'
            payload = {"text": asr_out.replace('<صخث>', ''), "source":src, "target":target}
            file_response = rq.post(url, headers = {'Content-Type': "application/json"}, json=payload)
            target_translation = file_response.json()['output']
            session['target_translation'] = target_translation

            with open(os.path.join(save_dir, output_dir, 'MT', 'trans.txt'), 'w') as f:
                f.write(target_translation + '\n')
            


        except Exception as e:
            print(e)
            print("ERROR FETCHING MT OUTPUT")
            session.pop('in_file', None)
            session.pop('asr_out', None)
            session.pop('trans_en', None)
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
        req = rq.post('https://farasa-api.qcri.org/msa/webapi/diacritizeV2', headers = {'content-type': "application/json"}, json=payload)
        diac_sent = req.json()['output']
        diac_sent = complete_tashkeel(diac_sent)
        session['diac_sent'] = diac_sent

        os.makedirs(os.path.join(save_dir, output_dir, 'TTS'))

        with open(os.path.join(save_dir, output_dir, 'TTS', 'diacritized_sent.txt'), 'w') as f:
                f.write(diac_sent + '\n')

        end = time.time()
        diac_time = end - start
        print("DIAC Time: " + str(diac_time))
    except:
        print("ERROR FETCHING DIAC OUTPUT")
        session.pop('in_file', None)
        session.pop('asr_out', None)
        session.pop('target_translation', None)
        session.pop('diac_sent', None)
        session.pop('out_male_file', None)
        session['error_message'] = 'There has been a problem with the diacritization. Please retry.'
        return render_template("record.html", error_message = session['error_message'] )

    ###################################### 5. TEXT TO SPEECH ######################################
    try:
        start = time.time()
        url = 'http://41.179.247.131:5000/'
        diac_sent = 'ي ' + diac_sent
        params = {'txt' : diac_sent, 'gender' : '0'}
        file_response = rq.post(url, params=params)
        out_male = 'out_male_{}.wav'.format(str(int(time.time())))
        out_female = 'out_female_{}.wav'.format(str(int(time.time())))

        with open(os.path.join(save_dir, output_dir, 'TTS', out_female), 'wb') as f:
            f.write(file_response.content)
        
        session['out_female_file'] = os.path.join( output_dir, 'TTS', out_female)

        url = 'http://41.179.247.131:5000/'
        params = {'txt' : diac_sent, 'gender' : '1'}
        file_response = rq.post(url, params=params)

        with open(os.path.join(save_dir, output_dir, 'TTS', out_male), 'wb') as f:
            f.write(file_response.content)
        
        session['out_male_file'] = os.path.join( output_dir, 'TTS', out_male)
        
        end = time.time()
        tts_time = end - start
        print("TTS Time: " + str(tts_time))
    except:
        print("ERROR FETCHING TTS OUTPUT")
        session.pop('in_file', None)
        session.pop('asr_out', None)
        session.pop('target_translation', None)
        session.pop('diac_sent', None)
        session.pop('out_male_file', None)
        session['error_message'] = 'There has been a problem with converting the text to speech. Please retry'
        return render_template("record.html", error_message=session['error_message'])
        
    print("Successfully Excuted the Pipeline")
    
    if do_trans == 'true':
        return render_template('record.html', 
                in_file = session['in_file'], 
                asr_out = session['asr_out'],
                target_translation = session['target_translation'],
                diac_sent = session['diac_sent'],
                out_male_file = session['out_male_file'])
    else:
        return render_template('record.html', 
            in_file = session['in_file'], 
            asr_out = session['asr_out'],
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
    except:
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
    except:
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
    except:
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
    except:
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
