"""
Marketing router — handles public form submissions (contact, demo booking).
"""
from typing import Optional
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, EmailStr
from app.utils.responses import success_response

router = APIRouter(prefix="/marketing", tags=["Marketing"])


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str


class DemoForm(BaseModel):
    name: str
    email: EmailStr
    company: str
    phone: str
    call_volume: str


def send_email_notification(subject: str, body: str):
    """Stub for sending email via SendGrid/SMTP"""
    print(f"EMAIL SENT: {subject} - {body}")


@router.post("/contact")
async def submit_contact_form(data: ContactForm, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(
        send_email_notification,
        "New Contact Request",
        f"From: {data.name} <{data.email}>\nMessage:\n{data.message}"
    )
    return success_response(message="Thanks for contacting us. We'll be in touch soon.")


@router.post("/book-demo")
async def book_demo(data: DemoForm, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(
        send_email_notification,
        "New Demo Request",
        f"From: {data.name} ({data.company})\nEmail: {data.email}\nPhone: {data.phone}\nVolume: {data.call_volume}"
    )
    return success_response(message="Demo request received. Our sales team will reach out shortly.")


@router.post("/pricing/inquiry")
async def pricing_inquiry(data: DemoForm, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(
        send_email_notification,
        "Enterprise Pricing Inquiry",
        f"From: {data.name} ({data.company})\nEmail: {data.email}\nPhone: {data.phone}\nVolume: {data.call_volume}"
    )
    return success_response(message="Pricing inquiry received. We'll send a custom quote soon.")
