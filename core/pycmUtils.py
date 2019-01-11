

def readable_timediff(seconds_diff, template='{value}{label}', labels=None):
    from dateutil.relativedelta import relativedelta
    
    if labels is None:
        labels = {'years': 'Y', 'months': 'M', 'days': 'D', 'hours': 'h', 'minutes': 'm', 'seconds': 's'}

    attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']

    if seconds_diff == 0:
        return ["0" + labels[attrs[-1]]]

    delta = relativedelta(seconds=seconds_diff)

    return [template.format(
        value=int(getattr(delta, attr)),
        label=(int(getattr(delta, attr)) > 1 and labels[attr] or labels[attrs[-1]])
    ) for attr in attrs if getattr(delta, attr, False)]


def create_ssh_client(server, port, user, password=None, key=None):
    import paramiko
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if not password is None:
        client.connect(server, port, user, password)
    else:
        client.connect(server, port, user, key_filename=key)

    return client

def remove_non_ascii(s):
    return "".join(i for i in s if ord(i) < 128)


def validate_email(email):
    import re

    EMAIL_REGEX = re.compile(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", re.IGNORECASE)

    return bool(EMAIL_REGEX.match(email))

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def send_email(config, email_to, subject, body, files):
    import smtplib

    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.application import MIMEApplication
    from os.path import basename


    toaddrs = email_to.split(",")
    #       msg = MIMEMultipart('alternative')
    msg = MIMEMultipart('mixed')

    msg['Subject'] = subject
    msg['From'] = config.EMAIL_USER
    msg['To'] = ", ".join(toaddrs)
    msg_part = MIMEText(body, 'html')
    msg.attach(msg_part)

    # Add attachements:
    for file_name in files or []:
        with open(file_name, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(file_name)
            )
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_name)
            msg.attach(part)

    s = smtplib.SMTP(config.EMAIL_SERVER_SSL, 587)
    s.connect(config.EMAIL_SERVER_SSL, 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
#    s = smtplib.SMTP(config.EMAIL_SERVER_SSL, 25)
    s.login(config.EMAIL_USER, config.EMAIL_PASS)
    # if DEBUG:
    #     s.set_debuglevel(1)
    s.sendmail(config.EMAIL_USER, toaddrs, msg.as_string())
    s.quit()


def plural(word):
    """
    Converts a word to its plural form.
    """
    if word in IRREGULAR_NOUNS:
        # foot->feet, person->people, etc
        return IRREGULAR_NOUNS[word]
    elif word.endswith('fe'):
        # wolf -> wolves
        return word[:-2] + 'ves'
    elif word.endswith('f'):
        # knife -> knives
        return word[:-1] + 'ves'
    elif word.endswith('o'):
        # potato -> potatoes
        return word + 'es'
    elif word.endswith('us'):
        # cactus -> cacti
        return word[:-2] + 'i'
    elif word.endswith('y'):
        # community -> communities
        return word[:-1] + 'ies'
    elif word[-1] in 'sx' or word[-2:] in ['sh', 'ch']:
        return word + 'es'
    elif word.endswith('an'):
        return word[:-2] + 'en'
    else:
        return word + 's'


IRREGULAR_NOUNS = {
    "addendum": "addenda",
    "aircraft": "aircraft",
    "alga": "algae",
    "alumna": "alumnae",
    "alumnus": "alumni",
    "amoeba": "amoebae",
    "analysis": "analyses",
    "antenna": "antennae",
    "antithesis": "antitheses",
    "apex": "apices",
    "appendix": "appendices",
    "automaton": "automata",
    "axis": "axes",
    "bacillus": "bacilli",
    "bacterium": "bacteria",
    "barracks": "barracks",
    "basis": "bases",
    "beau": "beaux",
    "bison": "bison",
    "buffalo": "buffalo",
    "bureau": "bureaus",
    "cactus": "cacti",
    "calf": "calves",
    "carp": "carp",
    "census": "censuses",
    "chassis": "chassis",
    "cherub": "cherubim",
    "child": "children",
    "château": "châteaus",
    "cod": "cod",
    "codex": "codices",
    "concerto": "concerti",
    "corpus": "corpora",
    "crisis": "crises",
    "criterion": "criteria",
    "curriculum": "curricula",
    "datum": "data",
    "deer": "deer",
    "diagnosis": "diagnoses",
    "die": "dice",
    "dwarf": "dwarfs",
    "echo": "echoes",
    "elf": "elves",
    "elk": "elk",
    "ellipsis": "ellipses",
    "embargo": "embargoes",
    "emphasis": "emphases",
    "erratum": "errata",
    "faux pas": "faux pas",
    "fez": "fezes",
    "firmware": "firmware",
    "fish": "fish",
    "focus": "foci",
    "foot": "feet",
    "formula": "formulae",
    "fungus": "fungi",
    "gallows": "gallows",
    "genus": "genera",
    "goose": "geese",
    "graffito": "graffiti",
    "grouse": "grouse",
    "half": "halves",
    "hero": "heroes",
    "hoof": "hooves",
    "hovercraft": "hovercraft",
    "hypothesis": "hypotheses",
    "index": "indices",
    "kakapo": "kakapo",
    "knife": "knives",
    "larva": "larvae",
    "leaf": "leaves",
    "libretto": "libretti",
    "life": "lives",
    "loaf": "loaves",
    "locus": "loci",
    "louse": "lice",
    "man": "men",
    "matrix": "matrices",
    "means": "means",
    "medium": "media",
    "memorandum": "memoranda",
    "millennium": "millennia",
    "minutia": "minutiae",
    "moose": "moose",
    "mouse": "mice",
    "nebula": "nebulae",
    "nemesis": "nemeses",
    "neurosis": "neuroses",
    "news": "news",
    "nucleus": "nuclei",
    "oasis": "oases",
    "offspring": "offspring",
    "opus": "opera",
    "ovum": "ova",
    "ox": "oxen",
    "paralysis": "paralyses",
    "parenthesis": "parentheses",
    "person": "people",
    "phenomenon": "phenomena",
    "phylum": "phyla",
    "pike": "pike",
    "polyhedron": "polyhedra",
    "potato": "potatoes",
    "prognosis": "prognoses",
    "quiz": "quizzes",
    "radius": "radii",
    "referendum": "referenda",
    "salmon": "salmon",
    "scarf": "scarves",
    "self": "selves",
    "series": "series",
    "sheep": "sheep",
    "shelf": "shelves",
    "shrimp": "shrimp",
    "spacecraft": "spacecraft",
    "species": "species",
    "spectrum": "spectra",
    "squid": "squid",
    "stimulus": "stimuli",
    "stratum": "strata",
    "swine": "swine",
    "syllabus": "syllabi",
    "symposium": "symposia",
    "synopsis": "synopses",
    "synthesis": "syntheses",
    "tableau": "tableaus",
    "that": "those",
    "thesis": "theses",
    "thief": "thieves",
    "tomato": "tomatoes",
    "tooth": "teeth",
    "trout": "trout",
    "tuna": "tuna",
    "vertebra": "vertebrae",
    "vertex": "vertices",
    "veto": "vetoes",
    "vita": "vitae",
    "vortex": "vortices",
    "watercraft": "watercraft",
    "wharf": "wharves",
    "wife": "wives",
    "wolf": "wolves",
    "woman": "women"
}
