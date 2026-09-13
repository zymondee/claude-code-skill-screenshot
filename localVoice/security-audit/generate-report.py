# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether, HRFlowable)

D = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DJ", D + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DJ-B", D + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DJ-M", D + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DJ", normal="DJ", bold="DJ-B")

INK   = colors.HexColor("#1b1f23")
MUTED = colors.HexColor("#5c6670")
RULE  = colors.HexColor("#d8dee4")
GREEN = colors.HexColor("#1a7f4b")
AMBER = colors.HexColor("#a9660a")
RED   = colors.HexColor("#b3261e")
BLUE  = colors.HexColor("#1f4e79")
BG    = colors.HexColor("#f3f5f7")

def S(name, **kw):
    base = dict(fontName="DJ", fontSize=9.5, leading=14.5, textColor=INK,
                alignment=TA_LEFT, spaceAfter=6)
    base.update(kw)
    return ParagraphStyle(name, **base)

st = {
 "title":  S("title", fontName="DJ-B", fontSize=21, leading=25, spaceAfter=3, textColor=BLUE),
 "sub":    S("sub", fontSize=10, textColor=MUTED, spaceAfter=16),
 "h1":     S("h1", fontName="DJ-B", fontSize=13.5, leading=17, spaceBefore=16, spaceAfter=7, textColor=BLUE),
 "h2":     S("h2", fontName="DJ-B", fontSize=10.5, leading=14, spaceBefore=9, spaceAfter=4),
 "body":   S("body"),
 "small":  S("small", fontSize=8.3, leading=12, textColor=MUTED),
 "cell":   S("cell", fontSize=8.5, leading=12, spaceAfter=0),
 "cellb":  S("cellb", fontName="DJ-B", fontSize=8.5, leading=12, spaceAfter=0),
 "cellh":  S("cellh", fontName="DJ-B", fontSize=8.5, leading=12, spaceAfter=0, textColor=colors.white),
 "bullet": S("bullet", leftIndent=11, bulletIndent=2, spaceAfter=3.5),
}

def P(t, s="body"): return Paragraph(t, st[s])
def B(t): return Paragraph(t, st["bullet"], bulletText="•")
def code(t): return '<font face="DJ-M" size="8.3">%s</font>' % t

def verdict_box(tone, head, text):
    c = {"ok": GREEN, "warn": AMBER, "bad": RED}[tone]
    bg = {"ok": colors.HexColor("#eaf6ef"), "warn": colors.HexColor("#fdf3e3"),
          "bad": colors.HexColor("#fdecea")}[tone]
    inner = [[Paragraph("<b>%s</b>" % head, S("vh", fontName="DJ-B", fontSize=10.5,
                                              leading=14, textColor=c, spaceAfter=3))],
             [Paragraph(text, S("vb", fontSize=9, leading=13.5, spaceAfter=0))]]
    t = Table(inner, colWidths=[163*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("LINEBEFORE", (0,0), (0,-1), 2.4, c),
        ("LEFTPADDING", (0,0), (-1,-1), 9), ("RIGHTPADDING", (0,0), (-1,-1), 9),
        ("TOPPADDING", (0,0), (-1,0), 8), ("BOTTOMPADDING", (0,-1), (-1,-1), 9),
        ("TOPPADDING", (0,1), (-1,1), 0), ("BOTTOMPADDING", (0,0), (-1,0), 2),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    return t

def table(header, rows, widths, aligns=None):
    data = [[Paragraph(h, st["cellh"]) for h in header]]
    for r in rows:
        data.append([Paragraph(c, st["cell"]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0,0), (-1,0), BLUE),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.4, RULE),
        ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0,i), (-1,i), BG))
    t.setStyle(TableStyle(style))
    return t

HEX = {"ok": "#1a7f4b", "warn": "#a9660a", "bad": "#b3261e", "info": "#1f4e79"}

def chip(tone, label):
    return '<font color="%s"><b>%s</b></font>' % (HEX[tone], label)

OK   = chip("ok", "Ren")
LOW  = chip("ok", "Låg")
MED  = chip("warn", "Medel")
INFO = chip("info", "Info")

story = []
A = story.append

# ── Rubrik ───────────────────────────────────────────────────────────────
A(P("Säkerhetsgranskning: VoiceStudio", "title"))
A(P("Repo <font face='DJ-M'>github.com/debpalash/VoiceStudio</font> · commit "
    "<font face='DJ-M'>eaf8bb9</font> · licens AGPL-3.0 · granskad 13 september 2026 · "
    "2 240 spårade filer", "sub"))

A(verdict_box("ok", "Slutsats: ingen skadlig kod hittad",
  "Jag hittade inga bakdörrar, inga dolda installationshakar, ingen obfuskerad kod, "
  "ingen inhämtning av lösenord/nycklar och ingen oannonserad utgående trafik. "
  "Tvärtom är projektet ovanligt säkerhetsmedvetet för att vara ett hobby-nära open source-projekt: "
  "det har egen SSRF- och DNS-rebinding-testsvit, gitleaks som blockerar merge, CodeQL, bandit och "
  "beroendegranskning i CI, samt en genomtänkt behörighetsmodell. "
  "Kvarstående risker är strukturella (osignerade Windows-installerare, modellfiler från Hugging Face, "
  "<font face='DJ-M'>curl | sh</font>-installation) — inte tecken på uppsåt."))
A(Spacer(1, 6))

# ── Analogi ──────────────────────────────────────────────────────────────
A(P("Kort analogi", "h1"))
A(P("Tänk på det som en husbesiktning. Jag har gått igenom grunden (finns det något inmurat som "
    "inte ska vara där?), elcentralen (vad kopplas ut från huset?), ytterdörrarna (vem kan komma in?) "
    "och besiktningsprotokollen från tidigare år (vad har andra redan hittat?). "
    "Huset är välbyggt och tidigare anmärkningar är åtgärdade. Det som återstår är att ytterdörren "
    "levereras utan certifierat lås i Windows-versionen, och att du själv bär in möbler "
    "(AI-modeller) från ett lager som du inte äger."))

# ── Metod ────────────────────────────────────────────────────────────────
A(P("1. Vad jag granskat", "h1"))
A(table(
  ["Område", "Vad jag letade efter", "Resultat"],
  [["Installationshakar",
    "<font face='DJ-M'>preinstall</font>/<font face='DJ-M'>postinstall</font>/<font face='DJ-M'>prepare</font> i samtliga "
    "<font face='DJ-M'>package.json</font> — klassiskt npm-kapningsmönster", "%s — noll förekomster" % OK],
   ["Droppers",
    "<font face='DJ-M'>curl … | bash</font> mot okända värdar, <font face='DJ-M'>base64 -d</font> vidarekopplat till skal, "
    "kodavkodning + <font face='DJ-M'>exec</font>", "%s — alla träffar är dokumenterade installerare mot egna/kända domäner" % OK],
   ["Kodexekvering",
    "<font face='DJ-M'>eval()</font>, <font face='DJ-M'>exec()</font>, <font face='DJ-M'>os.system()</font>, "
    "<font face='DJ-M'>shell=True</font>, <font face='DJ-M'>pickle.loads</font>, osäker <font face='DJ-M'>yaml.load</font>",
    "%s — inga träffar i backend eller skript" % OK],
   ["Nyckelstöld",
    "<font face='DJ-M'>~/.ssh</font>, <font face='DJ-M'>.aws/credentials</font>, <font face='DJ-M'>.netrc</font>, keychain, "
    "webbläsarkakor, plånboksfiler", "%s — inga träffar" % OK],
   ["Utgående trafik",
    "Samtliga domäner i körbar kod (py/js/ts/rs/sh/ps1) listade och klassade",
    "%s — endast Hugging Face, PyTorch, GitHub, egna domäner och opt-in-telemetri" % OK],
   ["Committade binärer",
    "ELF/Mach-O/PE-filer i git-historiken (klassiskt gömställe)", "%s — inga alls" % OK],
   ["CI-kedjan",
    "<font face='DJ-M'>pull_request_target</font>/<font face='DJ-M'>workflow_run</font> med utcheckning av PR-kod "
    "(\"pwn request\") och brett exponerade secrets", "%s — mönstret används inte; secrets bara i release/docker/evals" % OK],
   ["Nätverk",
    "Standardbindning, CORS, autentisering på API:et", "%s — loopback som standard, PIN/API-nyckel för LAN" % OK],
   ["Deserialisering",
    "<font face='DJ-M'>torch.load()</font> utan <font face='DJ-M'>weights_only</font> (pickle = kodexekvering)",
    "%s — 2 träffar, båda i utvärderingsverktyg" % MED]],
  [35*mm, 73*mm, 55*mm]))

# ── Telemetri ────────────────────────────────────────────────────────────
A(P("2. Vad som faktiskt lämnar din dator", "h1"))
A(P("Påståendet i inlägget du såg — <i>”ingen audio lämnar någonsin din dator”</i> — stämmer, och det "
    "är hårdare genomdrivet än marknadsföringstexten antyder. Det finns telemetri, men den är "
    "<b>avstängd som standard</b> och konstruerad så att den inte <i>kan</i> läcka innehåll:"))
A(B("<b>Två oberoende grindar</b> måste båda vara sanna: en konfigurerad mottagare <i>och</i> ditt "
    "uttryckliga val. Standardvärdet i koden är <font face='DJ-M'>False</font>."))
A(B("<b>Hård avstängning</b> med miljövariabeln <font face='DJ-M'>OMNIVOICE_ANALYTICS_DISABLED=1</font>, "
    "som slår ut båda grindarna."))
A(B("<b>Allowlist i koden</b>, inte i en policytext. Endast ~15 fält får passera "
    "(motor-id, språk, sekunder, <i>antal tecken</i> — aldrig texten, aldrig filnamn, aldrig röstnamn). "
    "Ett fält som inte står på listan kastas."))
A(B("<b>Autocapture och session recording är explicit avstängda</b> — SDK:ns standardläge skulle annars "
    "skicka texten du klickar på, vilket i den här appen är just manuset du ska syntetisera."))
A(B("<b>Stacktraces skickas medvetet inte</b>, eftersom de kan bära absoluta sökvägar och "
    "Hugging Face-tokens. Bara undantagets <i>klassnamn</i>."))
A(B("<b>Identitet</b> är ett slumpat UUID per installation — inte härlett från hårdvara, värdnamn "
    "eller användarnamn."))
A(Spacer(1, 3))
A(P("Mottagaren är PostHog på EU-värd (<font face='DJ-M'>eu.i.posthog.com</font>). "
    "Projekt-token ligger committad i klartext — det är avsiktligt och ofarligt: "
    "det är en <i>publishable</i> skrivnyckel som bara pekar ut en destination och inte kan läsa data. "
    "Avinstallationsskriptet skickar en sista <font face='DJ-M'>app_uninstalled</font>-signal, men "
    "endast om du var opt-in — annars skickas ingenting och inget skrivs ut.", "small"))

# ── Redan hittat ─────────────────────────────────────────────────────────
A(P("3. Vad andra redan har hittat", "h1"))
A(P("Det finns <b>inga publicerade säkerhetsråd (GitHub Security Advisories) och inga CVE:er</b> för "
    "projektet, och jag hittade inga användarrapporter om skadlig kod eller dataläckage. "
    "Däremot finns riktiga säkerhetsfynd som redan är <i>åtgärdade</i> — vilket är ett gott tecken, "
    "eftersom det visar att någon faktiskt tittar:"))
A(table(
  ["Fynd", "Vad det innebar", "Status"],
  [["Admin-rutter nåbara utan autentisering (#1213)",
    "I serverläge kunde en klient på ett betrott nätverk nå <font face='DJ-M'>/system/*</font> och "
    "<font face='DJ-M'>/api/settings/*</font> utan nyckel. Projektet klassar rutterna själv som "
    "”RCE-class” — alltså kodexekvering. Den korta delnings-PIN:en gav också admin.",
    "%s i v0.4.0. Kräver nyckel eller äkta loopback." % chip("ok", "Fixat")],
   ["35 + 5 beroendeaviseringar (#1456, #2030, #2031)",
    "Sårbarheter i Python- och Rust-beroenden, samt protobuf/transformers i CosyVoice 3.",
    "%s genom uppgraderingar" % chip("ok", "Fixat")],
   ["Ogiltig röstprofil kunde sparas (#1141)",
    "Fritext i ett profilfält kunde spara en profil som kraschade varje framtida generering — "
    "”återutnyttjat tre gånger via olika klienter”.",
    "%s — servern sanerar nu alla profiltyper" % chip("ok", "Fixat")],
   ["Osignerade Windows-installerare (#1712)",
    "Authenticode-signering av stabila Windows-installerare är avförd som <i>”not planned”</i>. "
    "SmartScreen kommer varna, och du kan inte kryptografiskt verifiera vem som byggt filen.",
    "%s — öppen, medveten avvägning" % chip("warn", "Ej planerat")],
   ["Saknad vattenstämpel i API (#1169)",
    "<font face='DJ-M'>/v1/audio/speech</font> returnerade omärkt ljud — regelefterlevnad "
    "(EU AI Act art. 50.2), inte en attackvektor.",
    "%s" % chip("ok", "Fixat")]],
  [40*mm, 85*mm, 38*mm]))

# ── Kvarstående risker ───────────────────────────────────────────────────
A(P("4. Kvarstående risker — rangordnade", "h1"))
A(table(
  ["#", "Risk", "Varför den finns", "Vad du gör åt den"],
  [["1", "Modellfiler från tredje part <font color='#a9660a'><b>(störst)</b></font>",
    "Appen laddar ner AI-modeller från Hugging Face. En <font face='DJ-M'>.pt</font>/"
    "<font face='DJ-M'>.bin</font>-fil är pickle-serialiserad Python och kan köra kod när den läses in. "
    "Det är hela ekosystemets problem, inte det här projektets.",
    "Håll dig till de motorer appen föreslår. Projektets egen säkerhetspolicy säger uttryckligen: "
    "aldrig privat distribuerade modellarkiv, aldrig körbara filer som följer med ett modellarkiv."],
   ["2", "Osignerad Windows-installer",
    "Ingen Authenticode-signatur. Du kan inte verifiera utgivaren i Windows, bara checksumman.",
    "På Windows: installera hellre från källkod, eller verifiera SHA256 mot "
    "<font face='DJ-M'>checksums</font>-filen i GitHub-releasen. macOS-bygget är notariserat."],
   ["3", "<font face='DJ-M'>curl … | sh</font>-installation",
    "Installationsskriptet gör SHA256-kontroll, men <i>hoppar över</i> den om inget "
    "<font face='DJ-M'>shasum</font>/<font face='DJ-M'>sha256sum</font> finns på maskinen — och "
    "checksum-filen kommer från samma källa som binären.",
    "Ladda ner skriptet först, läs det, kör det sedan. Eller klona repot och bygg från källkod — "
    "vilket du redan har gjort."],
   ["4", "<font face='DJ-M'>torch.load()</font> utan <font face='DJ-M'>weights_only</font>",
    "Två filer i <font face='DJ-M'>omnivoice/eval/</font> laddar checkpoints utan skyddet. "
    "Ingår inte i appens normala körväg — det är forskarverktyg för kvalitetsmätning.",
    "Ignorera om du bara kör appen. Kör inte eval-verktygen mot nedladdade checkpoints du inte litar på."],
   ["5", "LAN-delning",
    "Funktionen binder en andra server till <font face='DJ-M'>0.0.0.0</font> — men bara när du "
    "aktivt slår på den, och den är PIN-skyddad.",
    "Slå bara på den på nätverk du litar på. Exponera aldrig porten mot internet utan API-nyckel."],
   ["6", "Beroendeaviseringar blockerar inte merge",
    "<font face='DJ-M'>pip-audit</font> och <font face='DJ-M'>bun audit</font> rapporterar men stoppar "
    "inte en PR. Bara hemlighetsskanningen är blockerande.",
    "Medveten avvägning från projektet. Uppdatera regelbundet — de rensar aviseringar i praktiken."]],
  [7*mm, 33*mm, 63*mm, 60*mm]))

# ── Positivt ─────────────────────────────────────────────────────────────
A(P("5. Sånt som talar starkt för projektet", "h1"))
A(B("<b>Egen SSRF-testsvit.</b> Det finns tester som försöker lura appen att anropa "
    "<font face='DJ-M'>169.254.169.254</font> (molnleverantörers metadata-endpoint — klassisk "
    "nyckelstöld) och som simulerar <b>DNS-rebinding</b>, där en värd först svarar "
    "<font face='DJ-M'>127.0.0.1</font> och sedan något annat. Det är inte nybörjarnivå."))
A(B("<b>Hemlighetsskanning blockerar merge.</b> gitleaks är hård grind i CI; CodeQL, bandit och "
    "beroendegranskning kör på varje PR och veckovis."))
A(B("<b>Genomtänkt behörighetsmodell</b> med separata nivåer — anonym, loopback, betrott nät, PIN, "
    "API-nyckel, adminsession — i stället för ett enda \"är du inloggad\"-flagga."))
A(B("<b>Redigering är genomgående.</b> Egna moduler för sanering av felmeddelanden, sökvägssäkerhet, "
    "CSRF och diagnostikbuntar. Loggar HF-token-redigeras innan de visas."))
A(B("<b>Publik säkerhetspolicy</b> med privat rapporteringskanal och en uttrycklig policy om "
    "modellförsörjningskedjan."))
A(B("<b>AGPL-3.0</b> — ingen \"open source-tvätt\" med kommersiella tilläggsklausuler."))

# ── Rekommendation ───────────────────────────────────────────────────────
A(P("6. Min rekommendation till dig", "h1"))
A(verdict_box("ok", "Trygg att köra — med tre enkla vanor",
  "<b>1.</b> Kör från källkod (du har redan klonat repot som submodule), eller verifiera SHA256 om du "
  "hämtar en release.<br/>"
  "<b>2.</b> Låt telemetrin vara avstängd — den är det som standard. Vill du vara helt säker, sätt "
  "<font face='DJ-M'>OMNIVOICE_ANALYTICS_DISABLED=1</font>.<br/>"
  "<b>3.</b> Lägg aldrig till en modellfil från en privat källa, hur frestande erbjudandet än är. "
  "Det är den enda vägen in som projektet inte kan stänga åt dig."))
A(Spacer(1, 8))
A(P("En reservation, för hederlighetens skull: jag har granskat 2 240 filer med mönstersökning och "
    "riktad läsning av de säkerhetskritiska delarna — inte rad för rad genom hela kodbasen. "
    "En mycket välgömd bakdörr i en enskild motorintegration skulle kunna undgå den här metoden. "
    "Sannolikheten är låg med tanke på projektets öppenhet, CI-kedja och aktiva granskningsbottar, "
    "men den är inte noll.", "small"))

A(Spacer(1, 10))
A(HRFlowable(width="100%", thickness=0.5, color=RULE))
A(Spacer(1, 5))
A(P("<b>Källor:</b> lokal granskning av commit <font face='DJ-M'>eaf8bb9</font> · "
    "<font face='DJ-M'>CHANGELOG.md</font> · <font face='DJ-M'>.github/SECURITY.md</font> · "
    "<font face='DJ-M'>.github/workflows/security.yml</font> · "
    "GitHub Security Advisories (tom) · projektets issue-historik", "small"))

# ── Bygg ─────────────────────────────────────────────────────────────────
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "VoiceStudio-sakerhetsgranskning.pdf")

def deco(canv, doc):
    canv.saveState()
    canv.setFont("DJ", 7.5)
    canv.setFillColor(MUTED)
    canv.drawString(23*mm, 12*mm, "Säkerhetsgranskning · VoiceStudio @ eaf8bb9 · 2026-09-13")
    canv.drawRightString(A4[0]-23*mm, 12*mm, "Sida %d" % doc.page)
    canv.setStrokeColor(RULE); canv.setLineWidth(0.4)
    canv.line(23*mm, 15.5*mm, A4[0]-23*mm, 15.5*mm)
    canv.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, title="Säkerhetsgranskning – VoiceStudio",
                      author="Claude Code", subject="Säkerhets- och integritetsgranskning av debpalash/VoiceStudio",
                      leftMargin=23*mm, rightMargin=23*mm, topMargin=20*mm, bottomMargin=20*mm)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=deco)])
doc.build(story)
print("skrev", OUT)
