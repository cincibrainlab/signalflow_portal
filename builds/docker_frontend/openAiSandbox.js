const { OpenAI } = require('openai');

const openai = new OpenAI();

async function main() {
  const completion = await openai.chat.completions.create({
    messages: [{ role: "system", content: "You are a helpful assistant." }, { role: "user", content: "What is the fastest car?" }],
    model: "gpt-3.5-turbo",
  });
  console.log("Test Response");

  console.log(completion.choices[0]);
}

main();
