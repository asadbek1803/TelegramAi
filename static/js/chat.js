(() => {
  const thread = document.getElementById("thread");
  const emptyState = document.getElementById("emptyState");
  const form = document.getElementById("composer");
  const input = document.getElementById("input");
  const sendBtn = document.getElementById("sendBtn");
  const chips = document.getElementById("chips");

  const SESSION_KEY = "asadbekgpt.session";

  function sessionId() {
    let id = localStorage.getItem(SESSION_KEY);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(SESSION_KEY, id);
    }
    return id;
  }

  function newSession() {
    localStorage.setItem(SESSION_KEY, crypto.randomUUID());
  }

  if (window.Telegram?.WebApp) {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();
    document.documentElement.classList.add("in-telegram");
    try {
      tg.setHeaderColor("#111318");
      tg.setBackgroundColor("#111318");
    } catch (_) {
      /* eski Telegram versiyasi */
    }
  }

  if (window.marked) {
    marked.setOptions({ gfm: true, breaks: true });
  }

  function renderMarkdown(text) {
    if (!window.marked || !window.DOMPurify) {
      const div = document.createElement("div");
      div.textContent = text;
      return div.innerHTML;
    }
    return DOMPurify.sanitize(marked.parse(text));
  }

  function hideEmpty() {
    if (emptyState) emptyState.remove();
  }

  function addMessage(role, text = "", { error = false } = {}) {
    hideEmpty();
    const row = document.createElement("div");
    row.className = `msg ${role}${error ? " error" : ""}`;

    if (role === "assistant") {
      const av = document.createElement("div");
      av.className = "avatar";
      av.textContent = "AG";
      row.appendChild(av);
    }

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    if (text) bubble.innerHTML = renderMarkdown(text);
    row.appendChild(bubble);
    thread.appendChild(row);
    thread.scrollTop = thread.scrollHeight;
    return bubble;
  }

  function setBusy(busy) {
    sendBtn.disabled = busy;
    input.disabled = busy;
  }

  function resizeInput() {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
  }

  async function send(text) {
    const message = text.trim();
    if (!message) return;

    addMessage("user", message);
    input.value = "";
    resizeInput();
    setBusy(true);

    const bubble = addMessage("assistant");
    const cursor = document.createElement("span");
    cursor.className = "cursor";
    bubble.appendChild(cursor);

    let raw = "";
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId(), message }),
      });

      if (!res.ok || !res.body) {
        throw new Error("Server javob bermadi");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (const part of parts) {
          const line = part.split("\n").find((l) => l.startsWith("data: "));
          if (!line) continue;
          const data = line.slice(6);
          if (data === "[DONE]") continue;
          let payload;
          try {
            payload = JSON.parse(data);
          } catch {
            continue;
          }
          if (payload.error) {
            throw new Error(payload.error);
          }
          if (payload.delta) {
            raw += payload.delta;
            bubble.innerHTML = renderMarkdown(raw);
            bubble.appendChild(cursor);
            thread.scrollTop = thread.scrollHeight;
          }
        }
      }

      cursor.remove();
      if (!raw.trim()) {
        bubble.textContent = "Bo‘sh javob keldi. Qayta yozib ko‘ring.";
      } else {
        bubble.innerHTML = renderMarkdown(raw);
      }
    } catch (err) {
      cursor.remove();
      bubble.parentElement.classList.add("error");
      bubble.textContent = err.message || "Xatolik yuz berdi.";
    } finally {
      setBusy(false);
      input.focus();
    }
  }

  async function resetChat() {
    try {
      await fetch("/api/chat/new", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId() }),
      });
    } catch (_) {
      /* tarmoq xatosi — baribir UI tozalanadi */
    }
    newSession();
    location.reload();
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    send(input.value);
  });

  input.addEventListener("input", resizeInput);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  chips?.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-prompt]");
    if (btn) send(btn.dataset.prompt);
  });

  document.getElementById("newChatBtn")?.addEventListener("click", resetChat);
  document.getElementById("sideNewChat")?.addEventListener("click", resetChat);

  input.focus();
})();
