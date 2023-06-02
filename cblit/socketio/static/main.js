import { io } from "https://cdn.socket.io/4.6.1/socket.io.esm.min.js";
import {addChatMessage, addDocument, addPhrase} from "./ui.js";

const socket = io({
  autoConnect: false
});

function setWait(wait) {
  let spinner = document.getElementById("loading-spinner")
  if (wait) {
    spinner.hidden = false
  } else {
    spinner.hidden = true
  }
}

socket.on("connect", () => {
  console.log("connect", socket.connected); // true
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
  console.log("phrasebook", data)
  for (let phrase of data["phrases"]) {
    addPhrase(phrase["original"], phrase["translation"])
  }
})

socket.on("win", (dataString) => {
  let data = JSON.parse(dataString)
  console.log("win", data)
})

function giveDocument(index) {
  socket.emit("give_document", JSON.stringify({"index": index}))
}

function documentCallback() {}

console.log(socket)

socket.connect()
