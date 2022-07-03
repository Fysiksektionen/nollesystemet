from nollesystemet.models.settings import SiteSettings

def site_settings(request):
    return {'site_settings': SiteSettings.load()}
