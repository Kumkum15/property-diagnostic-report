let textUploaded = false
let imageUploaded = false

const textBtn = document.getElementById("textBtn")
const imageBtn = document.getElementById("imageBtn")

const textInput = document.getElementById("textPdf")
const imageInput = document.getElementById("imagePdf")

const generateBtn = document.getElementById("generateBtn")

const outputDiv = document.getElementById("reportOutput")

textBtn.onclick = () => textInput.click()
imageBtn.onclick = () => imageInput.click()


// ---------- TEXT PDF UPLOAD ----------

textInput.addEventListener("change", async () => {

const file = textInput.files[0]

const formData = new FormData()
formData.append("file", file)

const response = await fetch("http://127.0.0.1:8000/upload_text_pdf", {
method: "POST",
body: formData
})

const data = await response.json()

alert("Text PDF uploaded successfully")

textUploaded = true

})


// ---------- IMAGE PDF UPLOAD ----------

imageInput.addEventListener("change", async () => {

const file = imageInput.files[0]

const formData = new FormData()
formData.append("file", file)

const response = await fetch("http://127.0.0.1:8000/upload_image_pdf", {
method: "POST",
body: formData
})

const data = await response.json()

alert("Image PDF uploaded successfully")

imageUploaded = true

})


// ---------- GENERATE REPORT ----------

generateBtn.onclick = async () => {

if(!textUploaded || !imageUploaded){
alert("Please upload both PDFs first")
return
}

alert("Generating report...")

try{

const response = await fetch("http://127.0.0.1:8000/generate_report")

const data = await response.json()

console.log(data)

outputDiv.innerHTML = data.report

}catch(error){

console.error(error)

alert("Report generation failed")

}

}