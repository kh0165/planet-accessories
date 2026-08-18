function sendToWhatsApp(event) {

    event.preventDefault();

    const name = document.querySelector('[name="name"]').value;
    const email = document.querySelector('[name="email"]').value;
    const subject = document.querySelector('[name="subject"]').value;
    const message = document.querySelector('[name="message"]').value;

    const whatsappNumber = "201154924126";

    const text =
        "Hello Planet Accessories 👋\n\n" +
        "*New Contact Message*\n\n" +
        "*Name:* " + name + "\n" +
        "*Email:* " + email + "\n" +
        "*Subject:* " + subject + "\n\n" +
        "*Message:*\n" + message;

    const whatsappURL =
        "https://wa.me/" +
        whatsappNumber +
        "?text=" +
        encodeURIComponent(text);

    window.open(whatsappURL, "_blank");
}