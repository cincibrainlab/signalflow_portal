// uppyConfig.js
import Uppy from "@uppy/core";
import Dashboard from "@uppy/dashboard";
import RemoteSources from "@uppy/remote-sources";
import Webcam from "@uppy/webcam";
import ScreenCapture from "@uppy/screen-capture";
import GoldenRetriever from "@uppy/golden-retriever";
import Tus from "@uppy/tus";
import AwsS3 from "@uppy/aws-s3";
import AwsS3Multipart from "@uppy/aws-s3-multipart";
import XHRUpload from "@uppy/xhr-upload";
import ImageEditor from "@uppy/image-editor";
import DropTarget from "@uppy/drop-target";
import Audio from "@uppy/audio";
import Compressor from "@uppy/compressor";
import "@uppy/core/dist/style.css";
import "@uppy/dashboard/dist/style.css";
import "@uppy/audio/dist/style.css";
import "@uppy/screen-capture/dist/style.css";
import "@uppy/image-editor/dist/style.css";

const UPLOADER = "tus";
const COMPANION_URL = "http://companion.uppy.io";
const companionAllowedHosts = [];
const TUS_ENDPOINT = "http://0.0.0.0:3001/files/";
const XHR_ENDPOINT = "";
const RESTORE = true;

export const createUppyInstance = () => {
  const uppyDashboard = new Uppy({
    debug: false,
    restrictions: {
      allowedFileTypes: ['.set', '.fdt', '.fif']
    }
  })
    .use(Dashboard, {
      inline: true,
      target: "#app",
      showProgressDetails: true,
      proudlyDisplayPoweredByUppy: true,
      hideUploadButton: true,
      height: 200,
    })
    // .use(RemoteSources, {
    //   companionUrl: COMPANION_URL,
    //   sources: [
    //     "Box",
    //     "Dropbox",
    //     // "Facebook",
    //     "GoogleDrive",
    //     // "Instagram",
    //     "OneDrive",
    //     // "Unsplash",
    //     "Url",
    //   ],
    //   companionAllowedHosts,
    // })
    // .use(Webcam, {
    //   target: Dashboard,
    //   showVideoSourceDropdown: true,
    //   showRecordingLength: true,
    // })
    // .use(Audio, {
    //   target: Dashboard,
    //   showRecordingLength: true,
    // })
    // .use(ScreenCapture, { target: Dashboard })
    // .use(ImageEditor, { target: Dashboard })
    .use(DropTarget, {
      target: document.body,
    })
    .use(Compressor);

  switch (UPLOADER) {
    case "tus":
      uppyDashboard.use(Tus, { endpoint: TUS_ENDPOINT, limit: 6 });
      break;
    case "s3":
      uppyDashboard.use(AwsS3, { companionUrl: COMPANION_URL, limit: 6 });
      break;
    case "s3-multipart":
      uppyDashboard.use(AwsS3Multipart, {
        companionUrl: COMPANION_URL,
        limit: 6,
      });
      break;
    case "xhr":
      uppyDashboard.use(XHRUpload, {
        endpoint: XHR_ENDPOINT,
        limit: 6,
        bundle: true,
      });
      break;
    default:
  }

  if (RESTORE) {
    uppyDashboard.use(GoldenRetriever, { serviceWorker: true });
  }

  return uppyDashboard;
};