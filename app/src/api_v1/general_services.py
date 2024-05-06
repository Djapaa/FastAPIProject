import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Type
from email.header import Header

import aiosmtplib
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
import aiofiles

from ..config.model import Model
from ..config.settings import settings


async def get_object(session: AsyncSession, obj_id: int, model: Type['Model']):
    query = (
        select(model)
        .filter(model.id == obj_id)
    )
    obj = await session.scalar(query)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={
                                f'{model.__tablename__}': f'Invalid id {obj_id}, object not found'}
                            )
    return obj


async def upload_image(image: UploadFile, upload_subdir: str | None = None):
    if image.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    if not upload_subdir:
        upload_subdir = ''
    upload_dir = os.path.join(settings.MEDIA_ROOT, upload_subdir)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    dest = os.path.join(upload_dir, image.filename)

    content = await image.read()
    async with aiofiles.open(dest, 'wb') as out_file:
        await out_file.write(content)

    return dest


async def get_or_create(session: AsyncSession, model, defaults=None, **kwargs):
    instance = await session.execute(select(model).filter_by(**kwargs))
    instance = instance.scalar_one_or_none()
    if instance:
        return instance, False
    else:
        kwargs |= defaults or {}
        instance = model(**kwargs)

        try:
            session.add(instance)
            await session.commit()
        except Exception:
            await session.rollback()
            instance = await session.execute(select(model).filter_by(**kwargs))
            instance = instance.scalar_one()
            return instance, False
        else:
            return instance, True


MAIL_PARAMS = {
    'TLS': True,
    'host': settings.MAIL_HOST,
    'password': settings.MAIL_PASSWORD,
    'user': settings.MAIL_USERNAME,
    'port': settings.MAIL_PORT}


async def send_mail_async(to, subject, text, sender=settings.MAIL_FROM, textType='plain', **params):
    """Send an outgoing email with the given parameters.

    :param sender: From whom the email is being sent
    :type sender: str

    :param to: A list of recipient email addresses.
    :type to: list

    :param subject: The subject of the email.
    :type subject: str

    :param text: The text of the email.
    :type text: str

    :param textType: Mime subtype of text, defaults to 'plain' (can be 'html').
    :type text: str

    :param params: An optional set of parameters. (See below)
    :type params; dict

    Optional Parameters:
    :cc: A list of Cc email addresses.
    :bcc: A list of Bcc email addresses.
    """

    # Default Parameters
    cc = params.get("cc", [])
    bcc = params.get("bcc", [])
    mail_params = params.get("mail_params", MAIL_PARAMS)

    # Prepare Message
    msg = MIMEMultipart()
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = sender
    msg['To'] = ', '.join(to)
    if len(cc): msg['Cc'] = ', '.join(cc)
    if len(bcc): msg['Bcc'] = ', '.join(bcc)

    msg.attach(MIMEText(text, textType, 'utf-8'))

    # Contact SMTP server and send Message
    host = mail_params.get('host', 'localhost')
    isSSL = mail_params.get('SSL', False)
    isTLS = mail_params.get('TLS', False)
    if isSSL and isTLS:
        raise ValueError('SSL and TLS cannot both be True')
    port = mail_params.get('port', 465 if isSSL else 25)
    # For aiosmtplib 3.0.1 we must set argument start_tls=False
    # because we will explicitly be calling starttls ourselves when
    # isTLS is True:
    smtp = aiosmtplib.SMTP(hostname=host, port=port, start_tls=False, use_tls=isSSL)
    await smtp.connect()
    if isTLS:
        await smtp.starttls()
    if 'user' in mail_params:
        await smtp.login(mail_params['user'], mail_params['password'])
    await smtp.send_message(msg)
    await smtp.quit()


