window.CESIUM_BASE_URL = "../../Source/";

import {
  Cartesian3,
  createWorldTerrain,
  defined,
  formatError,
  Math as CesiumMath,
  objectToQuery,
  queryToObject,
  CzmlDataSource,
  GeoJsonDataSource,
  KmlDataSource,
  TileMapServiceImageryProvider,
  Viewer,
  viewerCesiumInspectorMixin,
  viewerDragDropMixin,
} from "../../Source/Cesium.js";

import * as Cesium from "../../Source/Cesium.js";

Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJkN2M3YTM1NC01ODcwLTQ4NDctODRiZC1iNmExMGNiNmQ3NzIiLCJpZCI6NjQzMjgsImlhdCI6MTYyOTExMDA5OH0.FERRrGiOOzThBx1XokWAAEIDCLG7MuF0Dh-QMccG_yY";
const terrainAssetID = 608730;
const osmBuildingAssetID = 96188;
const treeAssetID = 655651;
const lilleTorgetID_kristian = 655667;

const move_info = (viewer) => {

  // Information about the currently selected feature
  var selected = {
    feature: undefined,
    originalColor: new Cesium.Color(),
  };

  // An entity object which will hold info about the currently selected feature for infobox display
  var selectedEntity = new Cesium.Entity();

   // Get default left click handler for when a feature is not picked on left click
   var clickHandler = viewer.screenSpaceEventHandler.getInputAction(
    Cesium.ScreenSpaceEventType.LEFT_CLICK
  );

  // Silhouettes are supported
  var silhouetteBlue = Cesium.PostProcessStageLibrary.createEdgeDetectionStage();
  silhouetteBlue.uniforms.color = Cesium.Color.BLUE;
  silhouetteBlue.uniforms.length = 0.01;
  silhouetteBlue.selected = [];

  var silhouetteGreen = Cesium.PostProcessStageLibrary.createEdgeDetectionStage();
  silhouetteGreen.uniforms.color = Cesium.Color.LIME;
  silhouetteGreen.uniforms.length = 0.01;
  silhouetteGreen.selected = [];

  viewer.scene.postProcessStages.add(
    Cesium.PostProcessStageLibrary.createSilhouetteStage([
      silhouetteBlue,
      silhouetteGreen,
    ])
  );

  const originalLeftClickHandler = viewer.screenSpaceEventHandler.getInputAction(Cesium.ScreenSpaceEventType.LEFT_CLICK);
  // Silhouette a feature on selection and show metadata in the InfoBox.
  viewer.screenSpaceEventHandler.setInputAction(function onLeftClick(
    movement
  ) {

    originalLeftClickHandler(movement);

    // If a feature was previously selected, undo the highlight
    silhouetteGreen.selected = [];

    // Pick a new feature
    var pickedFeature = viewer.scene.pick(movement.position);
    console.log('pickedFeatured', pickedFeature);
    if (!Cesium.defined(pickedFeature)) {
      clickHandler(movement);
      return;
    }

    // Select the feature if it's not already selected
    if (silhouetteGreen.selected[0] === pickedFeature) {
      return;
    }

    // Save the selected feature's original color
    var highlightedFeature = silhouetteBlue.selected[0];
    if (pickedFeature === highlightedFeature) {
      silhouetteBlue.selected = [];
    }

    // Highlight newly selected feature
    silhouetteGreen.selected = [pickedFeature];

  },
  Cesium.ScreenSpaceEventType.LEFT_CLICK);
};

function entityChangedListen(viewer){
  viewer.selectedEntityChanged.addEventListener((e) => {
    console.log('entity changed');
    console.log(e);
  });
}

function leftClickOverride(viewer){
  console.log(viewer);
}

function custom(viewer, scene){

  var tileset = scene.primitives.add(
    new Cesium.Cesium3DTileset({
      url: Cesium.IonResource.fromAssetId(treeAssetID),
    })
  );  

  console.log('tileset 1', tileset);
    
  tileset.readyPromise
  .then(function (tileset) {
    viewer.zoomTo(
      tileset,
      new Cesium.HeadingPitchRange(
        0.5,
        -0.2,
        tileset.boundingSphere.radius * 4.0
      )
    );
  })
  .otherwise(function (error) {
    console.log(error);
  });

  var osmbuildingtileset = scene.primitives.add(
    new Cesium.Cesium3DTileset({
      url: Cesium.IonResource.fromAssetId(osmBuildingAssetID)
    })
  );

  console.log('tileset osmbuildings', osmbuildingtileset);

}


function main() {
  /*
     Options parsed from query string:
       source=url          The URL of a CZML/GeoJSON/KML data source to load at startup.
                           Automatic data type detection uses file extension.
       sourceType=czml/geojson/kml
                           Override data type detection for source.
       flyTo=false         Don't automatically fly to the loaded source.
       tmsImageryUrl=url   Automatically use a TMS imagery provider.
       lookAt=id           The ID of the entity to track at startup.
       stats=true          Enable the FPS performance display.
       inspector=true      Enable the inspector widget.
       debug=true          Full WebGL error reporting at substantial performance cost.
       theme=lighter       Use the dark-text-on-light-background theme.
       scene3DOnly=true    Enable 3D only mode.
       view=longitude,latitude,[height,heading,pitch,roll]
                           Automatically set a camera view. Values in degrees and meters.
                           [height,heading,pitch,roll] default is looking straight down, [300,0,-90,0]
       saveCamera=false    Don't automatically update the camera view in the URL when it changes.
     */
  var endUserOptions = queryToObject(window.location.search.substring(1));

  var imageryProvider;
  if (defined(endUserOptions.tmsImageryUrl)) {
    imageryProvider = new TileMapServiceImageryProvider({
      url: endUserOptions.tmsImageryUrl,
    });
  }

  var loadingIndicator = document.getElementById("loadingIndicator");
  var viewer;
  try {
    var hasBaseLayerPicker = !defined(imageryProvider);
    viewer = new Viewer("cesiumContainer", {
      imageryProvider: imageryProvider,
      baseLayerPicker: hasBaseLayerPicker,
      scene3DOnly: endUserOptions.scene3DOnly,
      requestRenderMode: true,
      terrainProvider: new Cesium.CesiumTerrainProvider({
        url: Cesium.IonResource.fromAssetId(terrainAssetID),
      })
    });


    if (hasBaseLayerPicker) {
      var viewModel = viewer.baseLayerPicker.viewModel;
     // viewModel.selectedTerrain = viewModel.terrainProviderViewModels[1];
    } 
  } catch (exception) {
    loadingIndicator.style.display = "none";
    var message = formatError(exception);
    console.error(message);
    if (!document.querySelector(".cesium-widget-errorPanel")) {
      //eslint-disable-next-line no-alert
      window.alert(message);
    }
    return;
  }

  viewer.extend(viewerDragDropMixin);
  if (endUserOptions.inspector) {
    viewer.extend(viewerCesiumInspectorMixin);
  }

  var showLoadError = function (name, error) {
    var title = "An error occurred while loading the file: " + name;
    var message =
      "An error occurred while loading the file, which may indicate that it is invalid.  A detailed error report is below:";
    viewer.cesiumWidget.showErrorPanel(title, message, error);
  };

  viewer.dropError.addEventListener(function (viewerArg, name, error) {
    showLoadError(name, error);
  });

  var scene = viewer.scene;
  var context = scene.context;
  if (endUserOptions.debug) {
    context.validateShaderProgram = true;
    context.validateFramebuffer = true;
    context.logShaderCompilation = true;
    context.throwOnWebGLError = true;
  }

  var view = endUserOptions.view;
  var source = endUserOptions.source;
  if (defined(source)) {
    var sourceType = endUserOptions.sourceType;
    if (!defined(sourceType)) {
      // autodetect using file extension if not specified
      if (/\.czml$/i.test(source)) {
        sourceType = "czml";
      } else if (
        /\.geojson$/i.test(source) ||
        /\.json$/i.test(source) ||
        /\.topojson$/i.test(source)
      ) {
        sourceType = "geojson";
      } else if (/\.kml$/i.test(source) || /\.kmz$/i.test(source)) {
        sourceType = "kml";
      }
    }

    var loadPromise;
    if (sourceType === "czml") {
      loadPromise = CzmlDataSource.load(source);
    } else if (sourceType === "geojson") {
      loadPromise = GeoJsonDataSource.load(source);
    } else if (sourceType === "kml") {
      loadPromise = KmlDataSource.load(source, {
        camera: scene.camera,
        canvas: scene.canvas,
        screenOverlayContainer: viewer.container,
      });
    } else {
      showLoadError(source, "Unknown format.");
    }

    if (defined(loadPromise)) {
      viewer.dataSources
        .add(loadPromise)
        .then(function (dataSource) {
          var lookAt = endUserOptions.lookAt;
          if (defined(lookAt)) {
            var entity = dataSource.entities.getById(lookAt);
            if (defined(entity)) {
              viewer.trackedEntity = entity;
            } else {
              var error =
                'No entity with id "' +
                lookAt +
                '" exists in the provided data source.';
              showLoadError(source, error);
            }
          } else if (!defined(view) && endUserOptions.flyTo !== "false") {
            viewer.flyTo(dataSource);
          }
        })
        .otherwise(function (error) {
          showLoadError(source, error);
        });
    }
  }

  if (endUserOptions.stats) {
    scene.debugShowFramesPerSecond = true;
  }

  var theme = endUserOptions.theme;
  if (defined(theme)) {
    if (endUserOptions.theme === "lighter") {
      document.body.classList.add("cesium-lighter");
      viewer.animation.applyThemeChanges();
    } else {
      var error = "Unknown theme: " + theme;
      viewer.cesiumWidget.showErrorPanel(error, "");
    }
  }

  if (defined(view)) {
    var splitQuery = view.split(/[ ,]+/);
    if (splitQuery.length > 1) {
      var longitude = !isNaN(+splitQuery[0]) ? +splitQuery[0] : 0.0;
      var latitude = !isNaN(+splitQuery[1]) ? +splitQuery[1] : 0.0;
      var height =
        splitQuery.length > 2 && !isNaN(+splitQuery[2])
          ? +splitQuery[2]
          : 300.0;
      var heading =
        splitQuery.length > 3 && !isNaN(+splitQuery[3])
          ? CesiumMath.toRadians(+splitQuery[3])
          : undefined;
      var pitch =
        splitQuery.length > 4 && !isNaN(+splitQuery[4])
          ? CesiumMath.toRadians(+splitQuery[4])
          : undefined;
      var roll =
        splitQuery.length > 5 && !isNaN(+splitQuery[5])
          ? CesiumMath.toRadians(+splitQuery[5])
          : undefined;

      viewer.camera.setView({
        destination: Cartesian3.fromDegrees(longitude, latitude, height),
        orientation: {
          heading: heading,
          pitch: pitch,
          roll: roll,
        },
      });
    }
  }

  var camera = viewer.camera;
  function saveCamera() {
    var position = camera.positionCartographic;
    var hpr = "";
    if (defined(camera.heading)) {
      hpr =
        "," +
        CesiumMath.toDegrees(camera.heading) +
        "," +
        CesiumMath.toDegrees(camera.pitch) +
        "," +
        CesiumMath.toDegrees(camera.roll);
    }
    endUserOptions.view =
      CesiumMath.toDegrees(position.longitude) +
      "," +
      CesiumMath.toDegrees(position.latitude) +
      "," +
      position.height +
      hpr;
    history.replaceState(undefined, "", "?" + objectToQuery(endUserOptions));
  }

  var timeout;
  if (endUserOptions.saveCamera !== "false") {
    camera.changed.addEventListener(function () {
      window.clearTimeout(timeout);
      timeout = window.setTimeout(saveCamera, 1000);
    });
  }

  loadingIndicator.style.display = "none";


  custom(viewer, scene);
  leftClickOverride(viewer);
  entityChangedListen(viewer);
  move_info(viewer);
}

main();
