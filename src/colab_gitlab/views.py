import os
import sys
from colab.plugins.views import ColabProxyView


class GitlabProxyView(ColabProxyView):
    app_label = 'colab_gitlab'
    diazo_theme_template = 'proxy/gitlab.html'
    rewrite = (
        (r'^/[^/]+/profile/password/edit/?$', 'password_change'),
    )


class GitlabProfileProxyView(ColabProxyView):
    app_label = 'colab_gitlab'
    diazo_theme_template = 'widgets/gitlab_profile.html'

    @property
    def diazo_rules(self):
        child_class_file = sys.modules[self.__module__].__file__
        app_path = os.path.abspath(os.path.dirname(child_class_file))
        diazo_path = os.path.join(app_path, 'widgets/profile/diazo.xml')

        self.log.debug("diazo_rules: %s", diazo_path)
        return diazo_path
