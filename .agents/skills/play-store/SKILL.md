---
name: play-store
description: >-
  Sign into Play Store on a Telephort device and install an app the person or
  the agent names. Use when the user asks to install, download, or update an
  app from Play Store, sign into Play Store, or pass a Play Store captcha.
  Does not create, start, or reconfigure the device.
compatibility: Any agent with the Telephort TypeScript or Python SDK. UI goes through device automation, not MCP.
---

# Play Store

Speak the user's language. This skill signs into Play Store and installs a store app. It does not create a device, start a stopped device, choose a device, or change its internet, model, GPU, or keybox. Those stay with the telephort-device skill.

Use the Telephort SDK in `sdk/typescript` or `sdk/python`. UI goes through `connectDeviceAutomation` (Python: `connect_device_automation`) and the accessibility tree (`a11y.find` / `a11y.tree`). Play Store package is `com.android.vending`.

Do not print or log the Play account password, the 2FA token, or a captcha API key. Do not commit `.cursor/skills/play-store/state.json`.

## Remembered state

Read and write `.cursor/skills/play-store/state.json`.

```json
{
  "play_account": null,
  "per_device": false,
  "devices": {},
  "captcha_keys": {},
  "left_services": [],
  "proven_service": null,
  "corrections": []
}
```

`play_account` is `email:password:2fa_token`. One account is used on every device until the person replaces it. `per_device: true` only after the person says each device has its own account; then `devices[deviceId]` holds that device's account and a device without one is asked. A service in `left_services` is not offered. `proven_service` is a service that has solved a Play sign-in captcha; offer it first. `corrections` are steps the person fixed; follow them on the next sign-in.

## Device and account

The person or the agent names the device. If they do not, ask. Do not pick a running device yourself.

If that device is not running, say so and wait. Do not call `devices.start`.

If Play Store is already signed in, do not sign in. Install on the account already there. Do not switch it.

If it is signed out, use the saved Play account. If none is saved, ask for `email:password:2fa_token` and save it. This is not the Shared Play account from the signup script.

## Controls

Act as soon as the target below is on screen. Do not dump the whole tree first, and do not tap a point from a screenshot.

A different device model can use different view ids and widget classes. The sign-in screens stay the same. Match the visible text on that screen. Do not reuse a view id, a class, or a tap point from another model. Confirm the node on this screen before the tap.

One action per screen. Do not tap that control again until the screen changes.

**Are you trying to sign in?** can appear at any moment: during sign-in, after it, over Play, or over another app. Tap **Yes, it's me**. Never tap **No, don't allow**. If the sheet is still there, the tap missed. Tap **Yes, it's me** again. This is not the **Yes** on **Check your phone**.

**Loading** or **indeterminate** means the buttons still listed are from the previous page. Do not tap them, including **I agree** and **Accept**. Wait until Loading is gone. **Yes, it's me** on **Are you trying to sign in?** is the current sheet, not a leftover button. Tap it.

**Checking info…** can stay while the next button is already there. Act on that button.

A UIAutomator dump is slow. Take one when the screen changes during sign-in. Do not take one on every download percent. The accessibility tree does not show this sign-in WebView. These screens come from UIAutomator.

If **Show password** or **Enter a password** is on screen, it is the password page, even when **Forgot email?** is still listed. Do not treat it as the email page.

On the password page the keyboard can be closed. Tap the `EditText` once. If the keyboard stays closed, tap one more point in that same rectangle. Do not tap **Show password**. Then one `input text` into the focused field. Do not type the password key by key: those taps missed the masked length, and a second key-by-key pass missed it again. If the masked length is still wrong, clear the field and `input text` once more. If it is still wrong, repeat the whole sign-in once with the same account. Do not change the field tap. On a 540×1200 model, a **Next** whose center sits at the bottom is under the keyboard. That tap types a key. Submit with `input keyevent 66`, or tap **Next** only when its center is above the keyboard.

`com.android.vending:id/0_resource_name_obfuscated` is on almost every Play Store node. It is not a target.

Type email, password, and the code with one `adb shell input text` into the field that is already focused. Do not type them key by key. Send `@` as `@`. A backslash before `@` is typed into this field. Replace a space with `%s`.

Send the email once. A second `input text` appends, so the field shows the address twice. The tree can leave `identifierId` text empty while the field already shows the address. Do not type again because that text is empty. Read the screen. Next is allowed only when the field shows one address, with `@` and no backslash. If it shows a backslash or the address twice, clear the field, then type once.

`identifierId` is already focused when the email screen opens. Do not tap it. A tap on that field is reported around 360,444 and lands on **Learn more**. Never tap `learnMore`, and never tap a node whose text contains `Learn more`.

Before `action.tap`, confirm the xpath matches a node. A tap with no match hits a default point.

`Next` on every sign-in page is `//node[@text='Next' and @class='android.widget.Button']`.

During sign-in, do not minimize Play. Tapping the system navigation bar minimizes it. Pressing Back while the keyboard is closed leaves the app. Both are bugs. Back (`input keyevent 4`) is only for an open keyboard, and that press only closes the keyboard.

Play can leave for the launcher on its own. That is normal. When `topResumedActivity` is the launcher, open `market://details?id=PACKAGE` again and continue from the Play screen that comes back. Do not start the sign-in steps over, and do not stop because that screen is an earlier page. If the dump lists **Home screen** while `com.android.vending` is still resumed, Play did not close. Wait, and do not send the link.

If the button this step needs is not visible, the keyboard is covering it. Press Back once only while the keyboard is open, then tap the button. Do not press Back when the keyboard is closed. Do not send the market link while Play is still in front. This includes the 2FA rows **Try another way** and **Google Authenticator**. Escape does not close the keyboard. `mInputShown=false` does not mean the keyboard is gone. If the button is already visible, do not press Back. Press Back only once for that button. If it is still missing and the keyboard is closed, stop and ask.

| When this is on screen | Do this |
| --- | --- |
| `//node[@text='Sign in' and @class='android.widget.Button']` | Tap it. On **Updating Google apps…** this button is already there. Do not wait for the update. Do not tap **Cancel updates**. On a 540×1200 model this button is missing from the accessibility tree and present in UIAutomator at physical pixels. `action.tap` halves those bounds and misses. Tap `input tap` at the node center. |
| `headingText` text is `Sign in with ease` | Tap `//node[@text='Skip' and @class='android.widget.Button']`. Do not tap Next. |
| `identifierId` | Do not tap the field. Input the email once into the focused field. Tap Next only when the screen shows one address, with `@` and no backslash. Never tap `learnMore`. |
| An `EditText` with no view id, and `selectionc6` (`Show password`) or **Enter a password** | This wins over **Forgot email?**. If the keyboard is closed, one tap in the `EditText`, then one more in the same rectangle only if it stays closed. Clear the field and send the password with one `input text`. Do not type it key by key. If the masked length differs, clear and `input text` once more. If it still differs, repeat the whole sign-in once. Then **Next**. If **Next** is not visible, press Back once to close the keyboard, then tap **Next**. Do not tap `selectionc6`. |
| **Are you trying to sign in?** with **Yes, it's me** | This sheet can cover any step, including another app. Tap `//node[@text="Yes, it's me" and @class='android.widget.Button']`. Do not tap **No, don't allow**. Do not open the app page from this screen. If the sheet is still there, tap **Yes, it's me** again. This is not the **Yes** on **Check your phone**. |
| `2-Step Verification` and **Check your phone** | The button is **Try another way**. Find it in the full UIAutomator node list. A shortened screen summary hides it. Tap that node. Do not tap **Yes** or **Resend it**. Do not open the app page from this screen. |
| 2-Step Verification chooser, and no node whose text is exactly `Google Authenticator` | That row is the button this step needs, and it is not visible. Press Back once to close the keyboard, then tap the row. |
| A node whose text is exactly `Google Authenticator` on the chooser, not inside a sentence | Tap the clickable row that contains that text. On the 540×1200 model that row is the `View` around y 768–881. Do not tap a zero-height text fragment. Do not tap the phone-code row `Use your phone or tablet to get a security code`. The row is visible, so do not press Back. |
| `totpPin`, **Enter code**, or **Get a verification code from the Google Authenticator app** | This is the code page. The words Google Authenticator here are a sentence, not the chooser row. Do not tap them. Do not press Back. Input the code from the 2FA token, tap Next. |
| `I agree` | Tap `//node[@text='I agree' and @class='android.widget.Button']`. Do not tap the Terms or Privacy links. |
| `Selfie for sign in` or `Add a selfie, just in case` | Tap the `Button` whose text is exactly `Not now`: `//node[@text='Not now' and @class='android.widget.Button']`. Confirm the xpath matches that button before the tap. A tap with no match hits the bottom-right button, which is **Continue** (seen at 585,1404). Never tap **Continue**. |
| `Can’t begin video verification` | Tap `//node[@text='Cancel']`. Do not tap **Try again**. |
| `Google services` with **More** | Tap `//node[@text='More']`. Do not change the Backup switch. |
| `Google services` with **Accept** and no **Cancel** | Tap `//node[@text='Accept' and @class='android.widget.Button']`. **Show more** is not **More**. Do not change the Backup switch. |
| `Welcome to Google Play` and **Get started** | Tap `//node[@text='Get started' and @class='android.widget.TextView']`. It is a `TextView`, not a `Button`. |
| `Make purchases in seconds` with **Skip** and **Continue** | Tap `//node[@text='Skip' and @class='android.widget.TextView']`. Do not tap **Continue**. |
| `Level up your experience` with **Not now** and **I'm in!** | Tap `//node[@text='Not now' and @class='android.widget.TextView']`. Do not tap **I'm in!**. |
| Package `com.google.android.apps.restore`, title `com.google.android.apps.restore:id/suc_layout_title` | Tap the `Button` whose text is `Don’t back up` (apostrophe U+2019). Do not clear the checkboxes. Do not tap **Turn on backup**. |
| A node whose text is exactly `No, thanks` | Tap that node, on every screen where it appears, including **Want to see local recommendations in Google Play?**. Do not tap **Continue**. |
| `//node[@text='Install']` | Tap it. It is a `TextView` with no view id. |

If the screen is one of these and its button is not visible, press Back once to close the keyboard and look again. If the button is still missing, stop and ask the person. Save the correction in `corrections`.

## Sign-in

If Play is already signed in, skip this section and install.

Signed in means Play is in front and the signed-out gate is gone. That gate is the screen **Sign in to find the latest Android apps**. Tabs such as **Games**, **Apps**, **Search**, and **You**, or an app sheet on top of them, mean the account is in. A node that merely says **Sign in** does not mean the gate is back. Do not start sign-in again.

1. `adb shell am start -a android.intent.action.VIEW -d market://details?id=PACKAGE`. Signed out, this is the Sign in gate. After sign-in, open that page only if it is not already showing. If **Install** is already on that app's page, tap it. Do not open the page again.
2. Tap **Sign in**. If **Are you trying to sign in?** appears here or at any later step, tap **Yes, it's me** before doing anything else.
3. Tap **Skip**.
4. Confirm the email screen (`identifierId`, **Forgot email?**, **Create account**). Do not tap the field. Input the email once, with `@` and no backslash. Tap **Next** only when the screen shows that one address. If the email page is still open after that Next, stop.
5. On **Show password** or **Enter a password**, clear the `EditText`, type the password once, then tap **Next**. If **Next** is not visible, press Back once to close the keyboard, then tap it. If the email page is still open after its own Next, stop.
6. On **Check your phone**, tap **Try another way**. Find that button in the full node list. On the chooser, tap the row whose text is exactly **Google Authenticator**. If that row is not visible, press Back once to close the keyboard, then tap the row. If the row is already visible, do not press Back. Do not open the app page until sign-in is finished.
7. On `totpPin` / **Enter code**, generate the code and input it. The sentence **Get a verification code from the Google Authenticator app** is this page, not the chooser. Tap **Next**. Do not press Back.

```bash
python3 .cursor/skills/play-store/scripts/totp.py <<'EOF'
PASTE_2FA_TOKEN
EOF
```

Generate it immediately before the input. If less than five seconds remain in the 30-second window, wait for the next code. If `scripts/totp.py` is not on disk, generate that same code in process. Do not stop because the helper path is missing.

8. Tap **I agree**.
9. On **Add a selfie, just in case**, tap the **Not now** button. Never tap **Continue**. If **Can’t begin video verification** appears, tap **Cancel**.
10. On **Google services**, tap **More** when that button is on screen, then **Accept** when **Cancel** is absent. **Show more** is not **More**. Do not change the Backup switch.
11. On **Welcome to Google Play**, tap **Get started**.
12. On **Make purchases in seconds**, tap **Skip**. Do not tap **Continue**.
13. On **Level up your experience**, tap **Not now**. Do not tap **I'm in!**.
14. Tap **Don’t back up**.
15. Whenever **No, thanks** is on screen, tap it. Do not tap **Continue**.

Sign-in is finished when that signed-out gate is gone and Play is in front. Then install. Find the app by a package link or by its title. Either way is enough. Do not treat one app's sheet as the proof of login, and do not look for a particular app before calling login done.

If the dump lists **Home screen** during sign-in, check `topResumedActivity`. When Play is still resumed, wait. When the launcher is resumed, Play left on its own. Open the same market link again and continue from the Play screen that appears. Do not go back to the first sign-in step, and do not treat that screen as a failed login.

A picture or a checkbox after any **Next** is a captcha. Handle it, then continue with the next target. `totpPin` is not a captcha.

## Captcha

Stop tapping. The internet on the device is a poor fit, whatever it already is: direct, a proxy, or a VPN. The person chooses one:

- Change the internet.
- A captcha service that understands this captcha.
- Solve it on the device.

**Change the internet.** Stop the sign-in. Do not edit the proxy, VPN, or direct setting. The telephort-device skill replaces the internet: the device is stopped, the new internet is checked, then the device is started. When it is running on that internet, start sign-in again from the beginning.

**Solve on the device.** Do not tap the captcha. Wait until it is gone, then continue.

**Service.** Offer only a service that can take the captcha on screen. If the type cannot be told from the tree, do not call a service. Say the type is unknown and offer an internet change or solving it on the device.

Order, skipping any name in `left_services`:

1. `proven_service`, if set.
2. CapSolver.
3. 2Captcha, after CapSolver was left.
4. Then the person picks from those not yet left: Anti-Captcha, CapMonster Cloud, SolveCaptcha, AZcaptcha, DeathByCaptcha.

RuCaptcha is 2Captcha. Do not offer it separately. Do not invent another service. Ask for that service's API key if `captcha_keys` does not have it, and save the key. A key is the only credential.

A failure is a Google rejection of the answer, a captcha type the service does not support, or a failed access. A timeout or a network error is a retry of the same attempt, not a failure.

After two Google rejections, or immediately on an unsupported type or a failed access, ask the person to keep this service or leave it. Leaving it adds the name to `left_services`. Keeping it after a failed access means a new API key; do not retry the rejected key. Keeping it after two rejections tries again, and two further rejections ask again.

When every service above has been left, the only choices are an internet change or solving the captcha on the device.

When a service solves the captcha, set `proven_service` to its name. Until one has, do not call any service sure to solve it.

## Install

A package opens its Play Store page directly. Do not search for a package.

```text
am start -a android.intent.action.VIEW -d market://details?id=PACKAGE
```

Run that with `adb_shell` on the automation session.

After that link, a dump can still list the launcher — **Home screen**, Google Go, Search — while Play is already in front. That dump does not mean Play closed. Read `dumpsys activity activities` and look for `topResumedActivity`. When it contains `com.android.vending`, do not send the link again. Wait for the Play page. Send the link again only when the resumed activity is the launcher.

A title is a normal case, not a fallback for one app. When there is no package, open Play search and use the title. If more than one result can be installed, ask which one. Do not install the first.

On that page:

- A price means the app is paid. Do not buy it. Tell the person.
- Already installed: say so. Do not install again.
- The package has no page: say it was not found. Do not pick a substitute.
- **Complete account setup** with **Continue** and no payment list: tap **Continue**.
- **Add a payment option to complete your account** with **Skip**: tap **Skip**. Do not tap **Add card**, **Add PayPal**, **Add PaysafeCard**, **Add Orange billing**, or **Redeem code**.
- **Link your Google services?** with **Get started**: press the device Back button once. If that sheet is still there, wait 2 seconds, tap **Get started**, then press the device Back button again. If that Back leaves Play and the launcher is resumed, do not press Back again. Open the market link and continue from the screen Play shows.
- Otherwise tap the node whose text is exactly `Install` on that app's page, once. Confirm that one node before the tap. Its class may be `Button`, `TextView`, or `View`. Do not tap it again.
- **Pending**, a percent, or **Installing** means the download has started. Poll `pm path PACKAGE`. Do not dump the UI on each poll. Open the same market link again only when `topResumedActivity` is the launcher. A dump that still lists **Home screen** while `com.android.vending` is resumed is not that case. If Play asks for the account password, input it the same way as the sign-in password.
- **Open** on that app's page is tapped once, with a finger on that node. If the page is still there, do not tap **Open** again. Start the installed app: `am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -p PACKAGE`.
- Finished when `pm path PACKAGE` prints `package:` and either that app is the resumed activity or its page showed **Open** and the launcher intent above was sent. A percent is not finished. **Open** on the launcher is not this button.
