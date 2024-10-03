import { API_HOST } from './config.js';

new Vue({
  el: '#app',
  data() {
    return {
      platform: localStorage.platform || 'harmony',
      serial: localStorage.serial || '', 
      devices: [],
      isConnected: false,
      isConnecting: false,
      isDumping: false,

      bundleName: localStorage.bundleName || "",
      abilityName: localStorage.abilityName || "",
      displaySize: localStorage.displaySize || [0, 0],
      jsonHierarchy: {},
    
      mouseClickCoordinatesPercent: null,

      hoveredNode: null,
      selectedNode: null,
      selectedNodeDetails: null,
      treeData: [],
      defaultProps: {
        children: 'children',
        label: 'type'
      },
      currentNodeId: "0",  //useless
      nodeFilterText: "",

      centerWidth: 500,
      isDividerHovered: false, // 用于跟踪拖动条是否被悬停
      isDragging: false // 用于跟踪是否正在拖动
    };
  },
  computed: {
    selectedNodeDetailsArray() {
      const defaultDetails = [
        { key: 'bundleName', value: this.bundleName },
        { key: 'abilityName', value: this.abilityName },
        { key: 'displaySize', value: this.displaySize },
        { key: '点击坐标 %', value: this.mouseClickCoordinatesPercent }
      ];
  
      if (!this.selectedNodeDetails) {
        return defaultDetails;
      }
  
      const nodeDetails = Object.keys(this.selectedNodeDetails)
        .filter(key => key !== 'children') // 过滤掉 children 字段
        .map(key => ({
          key,
          value: this.selectedNodeDetails[key]
        }));
  
      return [...defaultDetails, ...nodeDetails];
    }
  },
  watch: {
    platform: function (newval) {
      localStorage.setItem('platform', newval);
    },
    serial: function (newval) {
      localStorage.setItem('serial', newval);
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
    },
    listDevice: function () {
      $.ajax({
        method: "get",
        url: API_HOST + this.platform + "/serials"
      }).then(ret => {  
        this.devices = ret.data
      })
    },

    async connectDevice() {
      this.isConnecting = true;
      try {
        const platform = this.platform;
        const serial = this.serial;

        const response = await $.ajax({
          method: "post",
          url: API_HOST + platform + "/" + serial + "/init"
        });

        if (response.success) {
          this.isConnected = true;
          await this.dumpHierarchyWithScreen();
        } else {
          console.log(response.message)
          throw new Error(response.message);
        }
      } catch (err) {
        this.$message({showClose: true, message: `Error: ${err.message}`, type: 'error'});
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
        this.$message({showClose: true, message: `Error: ${err.message}`, type: 'error'});
      } finally {
        this.isDumping = false;
      }
    },

    async fetchScreenshot() {
      const platform = this.platform;
      const serial = this.serial;

      const response = await $.ajax({
        method: "get",
        url: API_HOST + platform + "/" + serial + "/screenshot"
      });

      if (response.success) {
        const base64Data = response.data;
        this.renderScreenshot(base64Data);
        localStorage.setItem('cachedScreenshot', base64Data);
      } else {
        throw new Error(response.message);
      }
    },

    async fetchHierarchy() {
      const platform = this.platform;
      const serial = this.serial;

      const response = await $.ajax({
        method: "get",
        url: API_HOST + platform + "/" + serial + "/hierarchy"
      });

      if (response.success) {
        const ret = response.data
        this.bundleName = ret.bundleName
        this.abilityName = ret.abilityName
        this.displaySize = ret.windowSize
        this.jsonHierarchy = ret.jsonHierarchy;
        this.treeData = [ret.jsonHierarchy];

        localStorage.setItem("bundleName", ret.bundleName);   
        localStorage.setItem("abilityName", ret.abilityName);
        localStorage.setItem("displaySize", ret.windowSize);

        this.hoveredNode = null; // 重置 hoveredNode
        this.selectedNode = null; // 重置 selectedNode
        this.selectedNodeDetails = null;
    
        this.renderHierarchy();
  
      } else {
        throw new Error(response.message);
      }
    },

    renderHierarchy() {
      const canvas = this.$el.querySelector('#hierarchyCanvas');
      const ctx = canvas.getContext('2d');
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
  
      // 获取缩放比例和位移
      const { scale, offsetX, offsetY } = this.screenshotTransform;
  
      // 设置虚线样式
      ctx.setLineDash([2, 6]); // 5px 实线，3px 空白
  
      // 递归绘制控件树
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
  
      // 绘制悬停节点的透明矩形区域
      if (this.hoveredNode) {
        const { x, y, width, height } = this.hoveredNode.rect;
        ctx.setLineDash([]);
        ctx.globalAlpha = 0.6;
        ctx.fillStyle = '#3679E3';
        ctx.fillRect(x * scale + offsetX, y * scale + offsetY, width * scale, height * scale);
        ctx.globalAlpha = 1.0;
      }
  
      // 绘制选中节点的实线矩形框
      if (this.selectedNode) {
        const { x, y, width, height } = this.selectedNode.rect;
        ctx.setLineDash([]);
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        ctx.strokeRect(x * scale + offsetX, y * scale + offsetY, width * scale, height * scale);
      }
    },
  
    loadCachedScreenshot() {
      const cachedScreenshot = localStorage.getItem('cachedScreenshot');
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
        
        // 保存缩放比例和位移
        this.screenshotTransform = { scale, offsetX: x, offsetY: y };
  
        // 清除画布并绘制图像
        ctx.clearRect(0, 0, canvasWidth, canvasHeight);
        ctx.drawImage(img, x, y, imgWidth * scale, imgHeight * scale);
  
        // 调整 hierarchyCanvas 的尺寸和位置
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
        this.selectedNode = selectedNode;
        this.selectedNodeDetails = selectedNode ? selectedNode : null; // 更新 selectedNodeDetails

        this.renderHierarchy();
  
        this.selectTreeNode(selectedNode._id); // FIXME
      }else{
        // 即使是同一个节点，也需要更新表格以显示新的坐标，触发重新渲染
        this.selectedNodeDetails = { ...this.selectedNodeDetails };
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
      this.selectedNodeDetails = node;
      this.renderHierarchy();
    },

    selectTreeNode(nodeId) {
      this.currentNodeId = nodeId;
      this.$nextTick().then(() => {
        this.$refs.treeRef.setCurrentKey(this.currentNodeId);
      });
    },

    filterNode(value, data) {
      if (!value) return true;
      if (!data || !data.type) return false; // 添加检查
      return data.type.indexOf(value) !== -1;   // TODO 兼容andorid/ios
    },

    copyToClipboard(value) {
      if (typeof value === 'object') {
        value = JSON.stringify(value, null, 2);
      }

      if (value === null || value === undefined || value === '') {
        value = '';
      }

      const textarea = document.createElement('textarea');
      textarea.value = value;
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand('copy');
        this.$message({showClose: true, message: "复制成功", type: 'success'});
      } catch (err) {
        this.$message({showClose: true, message: "复制失败", type: 'error'});
      }
      document.body.removeChild(textarea);
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