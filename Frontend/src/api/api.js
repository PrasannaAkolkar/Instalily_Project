export const getAIMessageStream = async (input, history, onChunk) => {
  const res = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: input, history }),
  });

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let content = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value);
    content += chunk;
    onChunk(content);  // update UI as we go
  }

  return { role: "assistant", content };
};

// export const getAIMessage = async (userQuery, history) => {
//   try {
//     const res = await fetch("http://localhost:8000/chat", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify({
//         message: userQuery,
//         history: history,
//       }),
//     });

//     const data = await res.json();
//     return {
//       role: "assistant",
//       content: data.response,
//     };
//   } catch (error) {
//     return {
//       role: "assistant",
//       content: "⚠️ Something went wrong contacting the assistant.",
//     };
//   }
// };
