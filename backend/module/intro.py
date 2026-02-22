# modules/intro.py
import io, os, uuid, base64, json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from gtts import gTTS

# --- Lesson Data ---
big_3_sequence = [
    # HABLAR
    ("We are going to practice the present simple", "en", None, 0),
    ("We use the present simple for things we do everyday", "en", None, 0),
    ("like doing the dishes, or going for a walk in the park", "en", None, 0),
    ("The present simple in Spanish is used in much the same way", "en", None, 0),
    ("Hablar,", "es", None, 0),
    ("is an AR verb which means to speak, and let us use this verb to illustrate", "en", None, 0),
    ("and how we say it in the first, second, and third person", "en", None, 0),
    ("I speak, in Spanish is ", "en", "v-yo-hablo", 0),
    ("You speak is ", "en", "v-tu-hablas", 0),
    ("He speaks is ", "en", "v-el-habla", 0),
    ("She speaks", "en", "v-ella-habla", 0),

    # MIRAR
    ("The verb Mirar means to watch. You will see the same rules apply here for this AR verb", "en", None, 1),
    ("I watch, in Spanish is ", "en", "v-yo-miro", 1),
    ("You watch, is ", "en", "v-tu-miras", 1),
    ("He watches is ", "en", "v-el-mira", 1),
    ("She watches", "en", "v-ella-mira", 1),

    # CAMINAR
    ("Another AR verb is Caminar and it means to walk. Again notice the verb endings, and how they end in O, AS, and A", "en", None, 2),
    ("I walk, in Spanish is ", "en", "v-yo-camino", 2),
    ("You walk, is ", "en", "v-tu-caminas", 2),
    ("He walks is ", "en", "v-el-camina", 2),
    ("She walks", "en", "v-ella-camina", 2),

    # ENSEÑAR
    ("And finally, Enseñar which means to teach.", "en", None, 3),
    ("I teach, in Spanish is ", "en", "v-yo-enseno", 3),
    ("You teach,  is ", "en", "v-tu-ensenas", 3),
    ("He teaches is ", "en", "v-el-ensena", 3),
    ("She teaches", "en", "v-ella-ensena", 3),
    ("Fantastic, now let us move onto the next section where the real learning starts", "en", None, 3),
]

verbs_data = {
    0: [["yo habl", "o"], ["tú habl", "as"], ["él habl", "a"], ["ella habl", "a"]],
    1: [["yo mir", "o"], ["tú mir", "as"], ["él mir", "a"], ["ella mir", "a"]],
    2: [["yo camin", "o"], ["tú camin", "as"], ["él camin", "a"], ["ella camin", "a"]],
    3: [["yo enseñ", "o"], ["tú enseñ", "as"], ["él enseñ", "a"], ["ella enseñ", "a"]],
}

# --- Function to register the route ---
def register_intro_routes(app: FastAPI):
    @app.get("/intro", response_class=HTMLResponse)
    async def serve_intro():
        items = []

        for text, lang, selector, g_idx in big_3_sequence:
            mp3 = io.BytesIO()
            gTTS(text, lang=lang).write_to_fp(mp3)
            mp3.seek(0)
            items.append({
                "audio": base64.b64encode(mp3.read()).decode(),
                "text": text,
                "selector": selector,
                "group": g_idx
            })

        payload_json = json.dumps({"items": items, "verbs": verbs_data})

        html_code = f"""
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        .outer-perimeter {{ max-width: 380px; margin: auto; border: 4px solid #2ecc71; border-radius: 25px; padding: 15px; background: #f9fdfb; font-family: sans-serif; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .box {{ background: white; border: 2px solid #2ecc71; border-radius: 15px; padding: 15px; margin-bottom: 15px; }}
        #script-box {{ min-height: 110px; text-align: center; display: flex; flex-direction: column; justify-content: center; }}
        #txt {{ font-size: 18px; color: #2c3e50; font-weight: 500; margin-top: 10px; line-height: 1.4; }}
        #verb-box {{ min-height: 240px; background: #fff; }}
        .v-row {{ padding: 12px; margin: 8px 0; font-size: 22px; border-radius: 10px; color: #bdc3c7; background: #fafafa; border: 1px solid #eee; text-align: center; }}
        .active {{ background: #f1c40f !important; color: #000 !important; font-weight: 900 !important; border: 2px solid #27ae60 !important; transform: scale(1.02); transition: 0.1s; }}
        .red-end {{ color: #e74c3c; font-weight: bold; }}
        canvas {{ width: 100%; height: 40px; }}
        .btn-go {{ width: 100%; padding: 20px; background: #2ecc71; color: white; border: none; border-radius: 40px; font-size: 20px; font-weight: 900; cursor: pointer; }}
        </style>

        <div class="outer-perimeter">
            <div class="box" id="script-box">
                <canvas id="wave"></canvas>
                <div id="txt">Welcome to the Spanish Lecture</div>
            </div>
            <div class="box" id="verb-box">
                <div id="list"></div>
            </div>
            <button id="start" class="btn-go">START LECTURE</button>
        </div>

        <script>
        const cvs = document.getElementById('wave');
        const ctx = cvs.getContext('2d');
        const txt = document.getElementById('txt');
        const list = document.getElementById('list');
        let data = {payload_json};
        let cur = 0, g = -1, raf;

        function draw() {{
            ctx.clearRect(0,0,cvs.width,cvs.height);
            ctx.strokeStyle = "#e74c3c";
            ctx.lineWidth = 3;
            ctx.beginPath();
            for(let x=0; x<cvs.width; x++) {{
                let y = cvs.height/2 + Math.sin(x*0.15 + Date.now()*0.02) * 10 * Math.random();
                if(x===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
            }}
            ctx.stroke();
            raf = requestAnimationFrame(draw);
        }}

        document.getElementById('start').onclick = () => {{
            document.getElementById('start').style.display = "none";
            play();
        }};

        function play() {{
            if(cur >= data.items.length) {{
                txt.innerText = "Lesson Complete!";
                list.innerHTML = "";
                cancelAnimationFrame(raf);
                return;
            }}

            const item = data.items[cur];
            txt.innerText = item.text;

            if(item.group !== g) {{
                g = item.group;
                list.innerHTML = "";
                (data.verbs[g] || []).forEach((v, i) => {{
                    let d = document.createElement('div');
                    d.className = 'v-row';
                    d.id = 'v-' + g + '-' + i;
                    d.innerHTML = v[0] + '<span class="red-end">' + v[1] + '</span>';
                    list.appendChild(d);
                }});
            }}

            document.querySelectorAll('.v-row').forEach(r => r.classList.remove('active'));
            if(item.selector) {{
                let idxMap = {{"yo":0, "tu":1, "el":2, "ella":3}};
                let parts = item.selector.split('-');
                let key = parts[1];
                let target = document.getElementById('v-' + g + '-' + idxMap[key]);
                if(target) target.classList.add('active');
            }}

            let audio = new Audio("data:audio/mp3;base64," + item.audio);
            draw();
            audio.onended = () => {{
                cancelAnimationFrame(raf);
                ctx.clearRect(0,0,cvs.width,cvs.height);
                cur++;
                setTimeout(play, 600);
            }};
            audio.play();
        }}
        </script>
        """

        return HTMLResponse(html_code)
