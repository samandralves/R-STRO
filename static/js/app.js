/* RASTRO — interações client-side, sem frameworks */

/* ---------------- HOME: check-in de humor ---------------- */
const RastroHome = {
  init() {
    const grid = document.getElementById("mood-grid");
    const feedback = document.getElementById("checkin-feedback");
    if (!grid) return;

    grid.addEventListener("click", async (e) => {
      const btn = e.target.closest(".mood-card");
      if (!btn) return;
      const mood = btn.dataset.mood;

      grid.querySelectorAll(".mood-card").forEach((c) => c.classList.remove("selected"));
      btn.classList.add("selected");

      try {
        const res = await fetch("/api/checkin", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mood }),
        });
        const data = await res.json();
        if (data.ok && feedback) {
          feedback.textContent = "Check-in registrado. Obrigado por compartilhar como você está.";
        }
      } catch (err) {
        if (feedback) feedback.textContent = "Não consegui registrar agora, mas obrigado por compartilhar.";
      }
    });
  },
};

/* ---------------- TALK: conversa em etapas ---------------- */
const RastroTalk = {
  init({ step }) {
    const log = document.getElementById("chat-log");
    const input = document.getElementById("chat-input");
    const sendBtn = document.getElementById("chat-send");
    const inputRow = document.getElementById("chat-input-row");
    if (!log) return;

    let currentStep = step || 0;
    let sending = false;

    function addBubble(html, from) {
      const div = document.createElement("div");
      div.className = `bubble ${from}`;
      div.innerHTML = html;
      log.appendChild(div);
      log.scrollTop = log.scrollHeight;
      return div;
    }

    function addOptions(options) {
      const wrap = document.createElement("div");
      wrap.className = "talk-options";
      options.forEach((opt) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "talk-option";
        btn.textContent = opt;
        btn.addEventListener("click", () => {
          wrap.remove();
          addBubble(opt, "user");
          sendToServer(opt);
        });
        wrap.appendChild(btn);
      });
      log.appendChild(wrap);
      log.scrollTop = log.scrollHeight;
    }

    function addResult(objective, barrier) {
      const div = document.createElement("div");
      div.className = "talk-result";
      div.innerHTML = `
        <span>✦</span>
        <div>
          <strong>Pronto! Seu 1% já está te esperando.</strong>
          <small>Objetivo: ${objective} · Barreira: ${barrier}</small>
        </div>`;
      log.appendChild(div);
      log.scrollTop = log.scrollHeight;
    }

    async function sendToServer(text) {
      if (sending) return;
      sending = true;
      try {
        const res = await fetch("/api/talk/answer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ step: currentStep, text }),
        });
        const data = await res.json();
        if (data.error) {
          sending = false;
          return;
        }

        currentStep = data.step;
        addBubble(data.reply, "rastro");

        if (data.options && data.options.length) {
          addOptions(data.options);
        }

        if (data.done) {
          inputRow.style.display = "none";
          addResult(data.objective, data.barrier);
          setTimeout(() => {
            window.location.href = data.redirect || "/onepct";
          }, 2200);
        }
      } catch (err) {
        addBubble("Tive um problema para responder agora. Tenta de novo?", "rastro");
      } finally {
        sending = false;
      }
    }

    function send() {
      const text = input.value.trim();
      if (!text) return;
      addBubble(text, "user");
      input.value = "";
      sendToServer(text);
    }

    sendBtn.addEventListener("click", send);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") send();
    });
  },
};

/* ---------------- 1%: metas ---------------- */
const RastroGoals = {
  init() {
    const list = document.getElementById("goal-list");
    if (!list) return;

    async function toggle(item) {
      const id = item.dataset.id;
      const res = await fetch("/api/goals/toggle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      const data = await res.json();
      const goal = data.goals.find((g) => String(g.id) === String(id));
      if (!goal) return;

      item.classList.toggle("done", goal.done);
      const check = item.querySelector(".goal-check");
      if (check) check.textContent = goal.done ? "✓" : "";

      const pointsValue = document.getElementById("points-value");
      if (pointsValue) pointsValue.textContent = `${data.points} pts`;

      const progressText = document.getElementById("progress-text");
      if (progressText) progressText.textContent = `${data.completed}/${data.goals.length} ações`;

      const progressBar = document.getElementById("goal-progress");
      if (progressBar) {
        const pct = data.goals.length ? (data.completed / data.goals.length) * 100 : 0;
        progressBar.style.width = `${pct}%`;
      }
    }

    list.addEventListener("click", (e) => {
      const item = e.target.closest(".goal");
      if (item) toggle(item);
    });

    list.addEventListener("keydown", (e) => {
      if (e.key !== "Enter" && e.key !== " ") return;
      const item = e.target.closest(".goal");
      if (item) {
        e.preventDefault();
        toggle(item);
      }
    });
  },
};

/* ---------------- SECRET: posts anônimos ---------------- */
const RastroSecret = {
  init() {
    const feed = document.getElementById("secret-feed");
    const textarea = document.getElementById("secret-textarea");
    const counter = document.getElementById("secret-counter");
    const postBtn = document.getElementById("secret-post-btn");
    if (!feed) return;

    if (textarea && counter) {
      textarea.addEventListener("input", () => {
        counter.textContent = `${textarea.value.length}/500`;
      });
    }

    postBtn.addEventListener("click", async () => {
      const text = textarea.value.trim();
      if (!text) return;

      const res = await fetch("/api/secret/post", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (!data.post) return;

      const article = document.createElement("article");
      article.className = "secret-post";
      article.dataset.id = data.post.id;
      article.innerHTML = `
        <p></p>
        <button class="secret-heart">♡ <span class="heart-count">0</span> <span>eu também</span></button>
        <button class="secret-report">denunciar</button>`;
      article.querySelector("p").textContent = data.post.text;
      feed.prepend(article);

      textarea.value = "";
      if (counter) counter.textContent = "0/500";
    });

    feed.addEventListener("click", async (e) => {
      const heartBtn = e.target.closest(".secret-heart");
      if (heartBtn) {
        const post = heartBtn.closest(".secret-post");
        const id = post.dataset.id;
        const res = await fetch("/api/secret/heart", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id }),
        });
        const data = await res.json();
        if (data.hearts !== undefined) {
          heartBtn.querySelector(".heart-count").textContent = data.hearts;
        }
        return;
      }

      const reportBtn = e.target.closest(".secret-report");
      if (reportBtn) {
        reportBtn.textContent = "denunciado";
        reportBtn.disabled = true;
        reportBtn.style.opacity = "0.5";
        reportBtn.style.cursor = "default";
      }
    });
  },
};