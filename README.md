<h1 align="center">Chat app with Python and sockets</h1>
<h3 align="center">This is my university project and I developed it.</h3>
Hello, this is a lesson project for the National University of Skills.
The goal of the project is to build a chat room using sockets and having GUL.
We run the program by creating a server file and send and listen to messages in it.
The client file enters the chat room by getting the username and starts chatting.
I also created a series of restrictions for the security part, which are very basic.
-Please message me if you have any new ideas because I want to implement this system for my website, which I wrote with Django.
<p align="center">
<a href="https://www.python.org" target="_blank"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/> </a>
<a href="https://www.sqlite.org/" target="_blank"> <img src="https://www.vectorlogo.zone/logos/sqlite/sqlite-icon.svg" alt="sqlite" width="40" height="40"/> </a>
</p>

# پروژه چت  –سرور و کلاینت با پایتون

## ۱. مقدمه
 این یک پروژه درسی هست که میخوایم اروز باهم تست کنیم و بریم جلو و چندتا مفاهیم جدید یادبگیریم.  
یک نکته جدید درمورد پایتون که یک چت روم ساده بسازی و هرکاربر با اسم خود وارد بشه و چیام بگذارد.  
 چت‌اپلیکیشن‌ها دقیقاً همین هدف را دنبال می‌کنند.  

این پروژه‌ی ساده‌ی **چت سرور – کلاینت با پایتون** برای نمایش عملی نحوه ایجاد یک سیستم پیام‌رسان طراحی شده است.  

###  اهداف پروژه:
- نشان دادن چگونگی ایجاد یک سرور مرکزی که چندین کاربر را مدیریت کند  
- اتصال چندین کلاینت به سرور و ارسال/دریافت پیام‌ها  
- داشتن رابط کاربری گرافیکی (`GUI`) ساده برای کاربران  
- بررسی اصول چندنخی (`Multi-threading`)  
- تمرین اصول برنامه‌نویسی امن و مدیریت خطا  



## ۲. مرور کلی پروژه
این پروژه از دو بخش اصلی تشکیل شده است:  

###  سرور (Server)
- مدیریت کاربران و اتصالات  
- دریافت پیام‌ها و پخش آن‌ها  
- پشتیبانی از چند اتصال همزمان با Threading  

###  کلاینت (Client)
- نام‌کاربری انتخاب می‌کند و وارد سیستم می‌شود  
- پیام عمومی یا خصوصی ارسال می‌کند  
- رابط گرافیکی ساده با **Tkinter**  

###  نحوه ارتباط
- کلاینت با **TCP Socket** به سرور وصل می‌شود  
- پیام ثبت‌نام (`register`) می‌فرستد  
- پیام‌های عمومی برای همه و پیام خصوصی فقط برای گیرنده ارسال می‌شوند  
- لیست کاربران همیشه به‌روز می‌شود  



## ۳. کتابخانه‌های استفاده‌شده
- **socket** → ایجاد ارتباط شبکه‌ای (TCP)  
- **threading** → چندریسمانی برای مدیریت چند کاربر  
- **tkinter** → ساخت رابط گرافیکی (GUI)  
- **json** → تبادل داده ساختاریافته بین کلاینت و سرور  
- **queue** → مدیریت صف پیام‌ها در کلاینت  
- **argparse** → گرفتن ورودی خط فرمان در سرور  
- **time** → درج زمان و مدیریت تأخیرها  



## ۴. ساختار سرور
- ایجاد سوکت (`socket.socket`)  
- `Bind` به آدرس و پورت  
- `Accept` اتصال‌ها در یک حلقه بی‌نهایت  
- ساخت یک `Thread` برای هر کاربر  
- مدیریت کاربران در یک دیکشنری `clients = {}`  
- ارسال پیام‌ها به‌صورت عمومی یا خصوصی  
- مدیریت خطاها و حذف کاربرانی که ناگهان قطع می‌شوند  



## ۵. ساختار کلاینت
- ثبت‌نام با ارسال پیام `{"type": "register", "user_id": "Ali"}`  
- ارسال پیام عمومی (`chat`)  
- ارسال پیام خصوصی (`pm`)  
- دریافت پیام‌ها با `Thread` جداگانه  
- مدیریت پیام‌ها با `queue`  
- درخواست لیست کاربران (`list`)  



## ۶. رابط کاربری (GUI)
با **Tkinter** ساخته شده و شامل:  
- پنجره ورود → نام کاربری و دکمه ورود  
- پنجره اصلی → نمایش پیام‌ها، ورودی پیام جدید  
- طراحی ساده ولی قابل توسعه   



## ۷. ویژگی‌های امنیتی
- استفاده از Lock برای جلوگیری از تداخل  
- جلوگیری از نام کاربری تکراری  
- مدیریت استثناها برای جلوگیری از کرش  
- حذف خودکار کاربران قطع‌شده  



## ۸. ذخیره تاریخچه پیام‌ها
- امکان ذخیره پیام‌ها در فایل متنی یا دیتابیس  
- در این پروژه فقط نمایش داده می‌شوند  



###  قابلیت‌های توسعه:
- ارسال فایل  
- احراز هویت با رمز عبور  
- رمزنگاری پیام‌ها  
- ساخت این چت باجنگو  
- ذخیره تاریخچه کامل گفتگوها  
- ساخت تیکت در وبسایت با پایتون و جنگو

---

##  اجرا

برای اجرای پروژه مراحل زیر را انجام دهید:

1. ابتدا سرور را اجرا کنید.  
   یک ترمینال باز کرده و دستور زیر را بزنید:

   ```bash
   python server.py
   ```

2. سپس کلانت را اجرا کرده.  

   ```bash
   python client.py
   ```


## ایمپورت‌ها

```bash
import argparse
```
- برای پارس‌کردن آرگومان‌های خط فرمان `(--host, --port, --cert, --key)`.

```bash
import json
```
- برای سریال‌سازی/دسریال‌سازی پیام‌ها به/از `JSON` (پروتکل انتقال ما).

```bash
import re
```
- برای اعتبارسنجی `user_id` با الگوی `Regex`.

```bash
import socket
```
- برای ساخت سوکت `TCP` (پایه‌ی ارتباط شبکه‌ای).

```bash
import ssl
```
- برای `TLS` اختیاری (رمزنگاری نشست `TCP`).

```bash
import threading
```
- برای اجرا/همزمانی: نخ پذیرش و نخ رسیدگی به هر کلاینت.

```bash
import time
```
- برای ثبت `timestamp` پیام‌ها، و حلقه‌ی اصلی.

```bash
from typing import Dict, Tuple, Optional
```
- تایپ‌هینت‌ها برای خوانایی و ایمنی بیشتر درکد.
```bash
import argparse
```
- دریافت `--host` و `--port` از خط فرمان.
```bash
import json, os, queue, socket, threading, time
```
- JSON برای پیام‌ها؛ OS برای مسیر تاریخچه؛ Queue برای صف thread-safe پیام‌ها؛ Socket برای ارتباط؛ Threading برای نخ دریافت؛ Time برای زمان‌بندی ساده.
```bash
import tkinter as tk و from tkinter import ttk, messagebox
```
- ساخت `GUI`، ویجت‌های مدرن `ttk`، و پیام‌های خطا/اطلاعاتی.
```bash
from datetime import datetime
```
- فرمت زمان در UI.
```bash
ENC = "utf-8" و BUFFER = 8192
```
- `UTF-8` استاندارد؛ `BUFFER` اینجا زیاد استفاده مستقیم ندارد چون از خط‌محور استفاده می‌کنیم (خوب است ولی حیاتی نیست).
```bash
import server
```
- این خط یعنی کلاینت می‌تواند سرور را هم استارت کند؛ برای پروژه آموزشی خوب است ولی برای محیط واقعی بهتر است جدا اجرا شوند (در ادامه اشاره شده).
```bash
def start_server_background(host, port):
```
- تابعی برای اجرای سرور در یک نخ پس‌زمینه، سپس `time.sleep(1)` تا فرصت بالا آمدن بدهد. مهم: استفاده‌اش اختیاری است؛ برای دمو در یک ماشین مفید است.

## تست پروژه
<p align="center">
<img src="https://raw.githubusercontent.com/sajadbazra/chat-room-python/refs/heads/main/demo/test-app.gif" alt="database schema" width="720"/>
</p>

## توضیح کوتاه خط های پروژه

### ثابت‌ها و تنظیمات پایه

```bash
ENC = "utf-8"
```
رمزگذاری استاندارد برای ارسال/دریافت متن.
```bash
MAX_LINE = 4096
```
حداکثر اندازه‌ی یک پیام/خط؛ از بمباران حافظه و پیام‌های غیرعادی جلوگیری می‌کند.
```bash
SOCKET_TIMEOUT = 15
```
تایم‌اوت عملیات سوکت (ثانیه)؛ برای جلوگیری از قفل‌شدن نامحدود.
```bash
BACKLOG = 100
```
صف اتصالات معلق در `listen()`؛ کنترل ظرفیت پذیرش.
```bash
USER_RE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
```
الگوی مجاز برای شناسه‌ی کاربری؛ فقط حروف/اعداد/خط زیر/خط تیره و حداکثر ۳۲ کاراکتر.

---

### امید وارم این پروژه برای شما مفید بوده باشه
- باتشکر از استاد مالک محمدی
