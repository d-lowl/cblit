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

    let msgTextElement = document.createElement("p")
    msgTextElement.textContent = message
    msgElement.appendChild(msgTextElement)

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
