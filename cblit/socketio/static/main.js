import { io } from "https://cdn.socket.io/4.6.1/socket.io.esm.min.js";
import {addChatMessage, addDocument, addPhrase, showBrief, showWin} from "./ui.js";

const socket = io({
  autoConnect: false
});

let finished = false;

function setWait(wait) {
  let spinner = document.getElementById("loading-spinner")
  let chat_input = document.getElementById("chat-input")
  let chat_submit = document.getElementById("chat-submit")
  let documents_submit = document.getElementsByClassName("document")
  spinner.hidden = !wait
  chat_input.disabled = wait || finished
  chat_submit.disabled = wait || finished
  for (let document_submit of documents_submit) {
    document_submit.disabled = wait || finished
  }
}

function initChat() {
  let chat_submit = document.getElementById("chat-submit")
  chat_submit.addEventListener("click", sayHandler)
  let chat_input = document.getElementById("chat-input")
  chat_input.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      sayHandler()
    }
  })
}

socket.on("connect", () => {
  console.log("connect", socket.connected); // true
  initChat()
});

socket.on("wait", (dataString) => {
  let data = JSON.parse(dataString)
  console.log("wait", data)
  setWait(data.wait)
})

socket.on("say", (dataString) => {
  let data = JSON.parse(dataString)
  console.log("say", data)
  let message = data.message
  addChatMessage("Officer", message, false)
})

socket.on("documents", (dataString) => {
  let data = JSON.parse(dataString)
  console.log("documents", data)
  for (let i in data["documents"]) {
    let doc = data["documents"][i]
    let docText = doc["text"]
    let docTitle = docText.split("\n")[0]
    let callback = () => {
      addChatMessage("You", `[give ${docTitle}]`, true)
      giveDocument(parseInt(i))
    }
    addDocument(doc["text"], callback)
  }
})

socket.on("phrasebook", (dataString) => {
  let data = JSON.parse(dataString)
  for (let phrase of data["phrases"]) {
    addPhrase(phrase["english"], phrase["conlang"])
  }
})

socket.on("win", (dataString) => {
  let data = JSON.parse(dataString)
  console.log("win", data)
  if (data["won"] === true) {
    finished = true
    setWait(false)
    showWin()
  }
})

socket.on("brief", (dataString) => {
  let data = JSON.parse(dataString)
  showBrief(data)
})

function giveDocument(index) {
  socket.emit("give_document", JSON.stringify({"index": index}))
}

function sayHandler() {
  let input = document.getElementById("chat-input")
  let msg = input.value
  input.value = ""
  addChatMessage("You", msg, true)
  say(msg)
}

function say(msg) {
  socket.emit("say", JSON.stringify({"who": "player", "message": msg}))
}

console.log(socket)

socket.connect()
