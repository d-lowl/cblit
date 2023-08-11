export function addChatMessage(sender, message, isRight) {
    let msgElement = document.createElement("div")
    msgElement.className = "chat-message bordered"

    let msgSenderElement = document.createElement("p")
    msgSenderElement.className = "chat-message-title"
    if (isRight) {
        msgSenderElement.className += " right"
    }
    msgSenderElement.textContent = sender
    msgElement.appendChild(msgSenderElement)

    for (let line of message.split("\n")) {
        let msgTextElement = document.createElement("p")
        msgTextElement.textContent = line
        msgElement.appendChild(msgTextElement)
    }

    let chatElement = document.getElementById("chat")
    chatElement.prepend(msgElement)
}

export function addPhrase(original, translation) {
    let text = `${original} --> ${translation}`
    let phraseElement = document.createElement("p")
    phraseElement.textContent = text
    let phrasebookElement = document.getElementById("phrasebook")
    phrasebookElement.appendChild(phraseElement)
}

export function addDocument(text, callback) {
    let documentElement = document.createElement("div")
    documentElement.className = "document bordered"
    documentElement.textContent = text
    documentElement.addEventListener("click", callback)
    let documentsElement = document.getElementById("documents")
    documentsElement.appendChild(documentElement)
}

export function showBrief(data) {
    addChatMessage("system", `Country: ${data["country_name"]}`)
    addChatMessage("system", data["country_description"])
    addChatMessage("system", `Language: ${data["language_name"]}`)
    addChatMessage("system", "You arrive to a new country. As an immigrant you need to register here. Good luck.")
}

export function showWin() {
    let msg = "The green light is lit! It appears you have successfully registered, " +
        "and can continue settling in the new country. Welcome."
    addChatMessage("system", msg, false)
}
