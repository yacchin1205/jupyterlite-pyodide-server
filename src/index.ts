import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'lite-redirect:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    if (window.location.pathname.includes('/lite/')) {
      return;
    }
    const baseUrl = app.serviceManager.serverSettings.baseUrl;
    window.location.replace(baseUrl + 'lite/');
  }
};

export default plugin;
