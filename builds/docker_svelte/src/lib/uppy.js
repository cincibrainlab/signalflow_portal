import Uppy from "@uppy/core";
import Dashboard from "@uppy/dashboard";
import GoldenRetriever from "@uppy/golden-retriever";
import Tus from "@uppy/tus";
import Compressor from "@uppy/compressor";

import "@uppy/core/dist/style.css";
import "@uppy/dashboard/dist/style.css";

const UPLOADER = "tus";
const TUS_ENDPOINT = "http://0.0.0.0:3001/files/";

export const createUppyInstance = () => {
  const uppyDashboard = new Uppy({
    debug: false,
    restrictions: {
      allowedFileTypes: ['.set', '.fdt', '.fif']
    }
  })
    .use(Dashboard, {
      inline: true,
      target: "#uppy-dashboard-container",
      showProgressDetails: true,
      proudlyDisplayPoweredByUppy: true,
      hideUploadButton: true,
      height: 200,
    })
    .use(Compressor)
    .use(Tus, { endpoint: TUS_ENDPOINT, limit: 6 })
    .use(GoldenRetriever, { serviceWorker: true });

  return uppyDashboard;
};