import { saveToLocalStorage, getFromLocalStorage, copyToClipboard } from './utils.js';
import { listDevices, connectDevice, fetchScreenshot, fetchHierarchy } from './api.js';


new Vue({
  el: '#app',
  data() {
    return {
      platform: getFromLocalStorage('platform', 'harmony'),
      serial: getFromLocalStorage('serial', ''),
      devices: [],
      isConnected: false,
      isConnecting: false,
      isDumping: false,
      wdaUrl: "",

      packageName: getFromLocalStorage('packageName', ''),
      activityName: getFromLocalStorage('activityName', ''),
      displaySize: getFromLocalStorage('displaySize', [0, 0]),
      jsonHierarchy: {},
      mouseClickCoordinatesPercent: null,
      hoveredNode: null,
      selectedNode: null,
      treeData: [],
      defaultProps: {
        children: 'children',
        label: '_type'
      },
      nodeFilterText: '',
      centerWidth: 500,
      isDividerHovered: false,
      isDragging: false
    };
  },
  computed: {
    selectedNodeDetails() {
      const isHarmony = this.platform === 'harmony';
      const defaultDetails = this.getDefaultNodeDetails(this.platform);

      if (!this.selectedNode) {
        return defaultDetails;
      }

      const nodeDetails = Object.keys(this.selectedNode)
        .filter(key => key !== 'children' && key !== '_id')
        .map(key => {
          let newKey = key;
          if (key === '_type') {
            newKey = isHarmony ? 'type' : 'class';
          }
          return {
            key: newKey,
            value: this.selectedNode[key]
          };
        });

      return [...defaultDetails, ...nodeDetails];
    }
  },
  watch: {
    platform(newVal) {
      saveToLocalStorage('platform', newVal);
    },
    serial(newVal) {
      saveToLocalStorage('serial', newVal);
    },
    nodeFilterText(val) {
      this.$refs.treeRef.filter(val);
    }
  },
  mounted() {
    this.loadCachedScreenshot();
    const canvas = this.$el.querySelector('#hierarchyCanvas');
    canvas.addEventListener('mousemove', this.onMouseMove);
    canvas.addEventListener('click', this.onMouseClick);
    canvas.addEventListener('mouseleave', this.onMouseLeave);
  },
  methods: {
    initPlatform() {
        this.serial = ''
        this.isConnected = false;
    },
    async listDevice() {
      try {
        const response = await listDevices(this.platform);
        this.devices = response.data;
      } catch (error) {
        console.error(error);
      }
    },
    async connectDevice() {
      this.isConnecting = true;
      try {
        if (!this.serial) {
          throw new Error('Please select device first');
        }

        const response = await connectDevice(this.platform, this.serial, this.wdaUrl);
        if (response.success) {
          this.isConnected = true;
          await this.dumpHierarchyWithScreen();
        } else {
          throw new Error(response.message);
        }
      } catch (err) {
        this.$message({ showClose: true, message: `Error: ${err.message}`, type: 'error' });
      } finally {
        this.isConnecting = false;
      }
    },
    async dumpHierarchyWithScreen() {
      this.isDumping = true;
      try {
        await this.fetchScreenshot();
        await this.fetchHierarchy();
      } catch (err) {
        this.$message({ showClose: true, message: `Error: ${err.message}`, type: 'error' });
      } finally {
        this.isDumping = false;
      }
    },
    async fetchScreenshot() {
      try {
        const response = await fetchScreenshot(this.platform, this.serial);
        if (response.success) {
          const base64Data = response.data;
          this.renderScreenshot(base64Data);
          saveToLocalStorage('cachedScreenshot', base64Data);
        } else {
          throw new Error(response.message);
        }
      } catch (error) {
        console.error(error);
      }
    },
    async fetchHierarchy() {
      try {
        const response = await fetchHierarchy(this.platform, this.serial);
        if (response.success) {
          const ret = response.data;
          this.packageName = ret.packageName;
          this.activityName = ret.activityName;
          this.displaySize = ret.windowSize;
          this.jsonHierarchy = ret.jsonHierarchy;
          this.treeData = [ret.jsonHierarchy];

          saveToLocalStorage('packageName', ret.packageName);
          saveToLocalStorage('activityName', ret.activityName);
          saveToLocalStorage('displaySize', ret.windowSize);

          this.hoveredNode = null;
          this.selectedNode = null;

          this.renderHierarchy();
        } else {
          throw new Error(response.message);
        }
      } catch (error) {
        console.error(error);
      }
    },
    renderHierarchy() {
      const canvas = this.$el.querySelector('#hierarchyCanvas');
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const { scale, offsetX, offsetY } = this.screenshotTransform;
      ctx.setLineDash([2, 6]);

      const drawNode = (node) => {
        if (node.rect) {
          const { x, y, width, height } = node.rect;
          ctx.strokeStyle = 'red';
          ctx.lineWidth = 0.8;
          ctx.strokeRect(x * scale + offsetX, y * scale + offsetY, width * scale, height * scale);
        }
        if (node.children) {
          node.children.forEach(drawNode);
        }
      };

      drawNode(this.jsonHierarchy);

      if (this.hoveredNode) {
        const { x, y, width, height } = this.hoveredNode.rect;
        ctx.setLineDash([]);
        ctx.globalAlpha = 0.6;
        ctx.fillStyle = '#3679E3';
        ctx.fillRect(x * scale + offsetX, y * scale + offsetY, width * scale, height * scale);
        ctx.globalAlpha = 1.0;
      }

      if (this.selectedNode) {
        const { x, y, width, height } = this.selectedNode.rect;
        ctx.setLineDash([]);
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        ctx.strokeRect(x * scale + offsetX, y * scale + offsetY, width * scale, height * scale);
      }
    },
    loadCachedScreenshot() {
      const cachedScreenshot = getFromLocalStorage('cachedScreenshot', null);
      if (cachedScreenshot) {
        this.renderScreenshot(cachedScreenshot);
      }
    },
    renderScreenshot(base64Data) {
      const img = new Image();
      img.src = `data:image/png;base64,${base64Data}`;
      img.onload = () => {
        const canvas = this.$el.querySelector('#screenshotCanvas');
        const ctx = canvas.getContext('2d');

        const { clientWidth: canvasWidth, clientHeight: canvasHeight } = canvas;
        canvas.width = canvasWidth;
        canvas.height = canvasHeight;

        const { width: imgWidth, height: imgHeight } = img;
        const scale = Math.min(canvasWidth / imgWidth, canvasHeight / imgHeight);
        const x = (canvasWidth - imgWidth * scale) / 2;
        const y = (canvasHeight - imgHeight * scale) / 2;

        this.screenshotTransform = { scale, offsetX: x, offsetY: y };

        ctx.clearRect(0, 0, canvasWidth, canvasHeight);
        ctx.drawImage(img, x, y, imgWidth * scale, imgHeight * scale);

        const hierarchyCanvas = this.$el.querySelector('#hierarchyCanvas');
        hierarchyCanvas.width = canvasWidth;
        hierarchyCanvas.height = canvasHeight;
      };
    },
    findSmallestNode(node, mouseX, mouseY, scale, offsetX, offsetY) {
      let smallestNode = null;

      const checkNode = (node) => {
        if (node.rect) {
          const { x, y, width, height } = node.rect;
          const scaledX = x * scale + offsetX;
          const scaledY = y * scale + offsetY;
          const scaledWidth = width * scale;
          const scaledHeight = height * scale;

          if (mouseX >= scaledX && mouseY >= scaledY && mouseX <= scaledX + scaledWidth && mouseY <= scaledY + scaledHeight) {
            if (!smallestNode || (width * height < smallestNode.rect.width * smallestNode.rect.height)) {
              smallestNode = node;
            }
          }
        }
        if (node.children) {
          node.children.forEach(checkNode);
        }
      };

      checkNode(node);
      return smallestNode;
    },
    getDefaultNodeDetails(platform) {
      const commonDetails = [
        { key: 'displaySize', value: this.displaySize },
        { key: '点击坐标 %', value: this.mouseClickCoordinatesPercent }
      ];
    
      switch (platform) {
        case 'ios':
          return [
            { key: 'bundleId', value: this.packageName },
            ...commonDetails
          ];
        case 'android':
          return [
            { key: 'packageName', value: this.packageName },
            { key: 'activityName', value: this.activityName },
            ...commonDetails
          ];
        case 'harmony':
          return [
            { key: 'packageName', value: this.packageName },
            { key: 'pageName', value: this.activityName },
            ...commonDetails
          ];
        default:
          return commonDetails;
      }
    },
    onMouseMove(event) {
      const canvas = this.$el.querySelector('#hierarchyCanvas');
      const rect = canvas.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;

      const { scale, offsetX, offsetY } = this.screenshotTransform;

      const hoveredNode = this.findSmallestNode(this.jsonHierarchy, mouseX, mouseY, scale, offsetX, offsetY);
      if (hoveredNode !== this.hoveredNode) {
        this.hoveredNode = hoveredNode;
        this.renderHierarchy();
      }
    },
    onMouseClick(event) {
      const canvas = this.$el.querySelector('#hierarchyCanvas');
      const rect = canvas.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;

      const { scale, offsetX, offsetY } = this.screenshotTransform;

      const percentX = (mouseX / canvas.width);
      const percentY = (mouseY / canvas.height);

      this.mouseClickCoordinatesPercent = `(${percentX.toFixed(2)}, ${percentY.toFixed(2)})`;

      const selectedNode = this.findSmallestNode(this.jsonHierarchy, mouseX, mouseY, scale, offsetX, offsetY);
      if (selectedNode !== this.selectedNode) {
        this.selectedNode = selectedNode ? selectedNode : null;

        this.renderHierarchy();

      } else {
        // 保证每次点击重新计算`selectedNodeDetails`，更新点击坐标
        this.selectedNode = { ...this.selectedNode };
      }
    },
    onMouseLeave() {
      if (this.hoveredNode) {
        this.hoveredNode = null;
        this.renderHierarchy();
      }
    },
    handleTreeNodeClick(node) {
      this.selectedNode = node;
      this.renderHierarchy();
    },
    filterNode(value, data) {
      if (!value) return true;
      if (!data || !data._type) return false;
      return data._type.indexOf(value) !== -1;
    },
    copyToClipboard(value) {
      const success = copyToClipboard(value);
      this.$message({ showClose: true, message: success ? "复制成功" : "复制失败", type: success ? 'success' : 'error' });
    },
    startDrag(event) {
      this.isDragging = true;
      document.addEventListener('mousemove', this.onDrag);
      document.addEventListener('mouseup', this.stopDrag);
    },
    onDrag(event) {
      this.centerWidth = event.clientX - this.$el.querySelector('.left').offsetWidth;
    },
    stopDrag() {
      this.isDragging = false;
      document.removeEventListener('mousemove', this.onDrag);
      document.removeEventListener('mouseup', this.stopDrag);
    },
    hoverDivider() {
      this.isDividerHovered = true;
    },
    leaveDivider() {
      this.isDividerHovered = false;
    }
 }
});