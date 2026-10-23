export function responseOutputText(payload) {
  if (typeof payload?.output_text === "string") return payload.output_text.trim();
  return (payload?.output || []).flatMap((item) => item.content || [])
    .filter((content) => content.type === "output_text" && typeof content.text === "string")
    .map((content) => content.text)
    .join("\n")
    .trim();
}

export async function requestOpenAi({ apiKey, body, timeoutMs = 120000, operation = "geração" }) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  let response;
  try {
    response = await fetch("https://api.openai.com/v1/responses", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`
      },
      body: JSON.stringify(body),
      signal: controller.signal
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(`A ${operation} ultrapassou dois minutos. Tente novamente.`);
    }
    throw new Error("Não foi possível conectar à API da OpenAI. Confira sua conexão e tente novamente.");
  } finally {
    clearTimeout(timeout);
  }

  if (!response.ok) {
    let detail = "";
    try {
      const payload = await response.json();
      detail = typeof payload?.error?.message === "string"
        ? payload.error.message.trim().slice(0, 400)
        : "";
    } catch (_error) {
      // Status and operation still provide a useful error.
    }
    if (response.status === 401) throw new Error("Chave rejeitada. Abra 🔑 API e confira a chave.");
    if (response.status === 429) throw new Error("O limite da API foi atingido. Tente novamente mais tarde.");
    throw new Error(`A OpenAI recusou a ${operation} (erro ${response.status}).${detail ? ` ${detail}` : ""}`);
  }
  return response.json();
}
