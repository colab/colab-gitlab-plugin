from colab.widgets.widget_manager import WidgetManager

from colab_gitlab.widgets.profile.profile import GitlabProfileWidget

WidgetManager.register_widget('profile', GitlabProfileWidget())
