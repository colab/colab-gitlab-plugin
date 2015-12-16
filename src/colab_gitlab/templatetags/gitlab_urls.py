from django import template

register = template.Library()


@register.assignment_tag()
def profile_url(user, user_url):
    if not user:
        return ""

    html = '- <a href="{url}">{user}</a>'.format(url=user_url,
                                                 user=user.title())
    return html
