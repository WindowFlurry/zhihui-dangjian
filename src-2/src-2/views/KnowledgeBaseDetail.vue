<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const knowledgeBaseId = route.params.id

// 模拟知识库
const knowledgeBaseData = ref({
  id: '',
  name: '',
  description: '',
  createdAt: '',
  files: []
})

// 当前查看的文件内容
const currentFileContent = ref('')
const currentFileName = ref('')
const currentFileIndex = ref(-1)

// 模拟文件内容 - 党建相关内容
const fileContents = [
  {
    id: 1,
    name: '中国共产党章程全文.docx',
    content: '# 中国共产党章程\n\n## 总纲\n\n中国共产党是中国工人阶级的先锋队，同时是中国人民和中华民族的先锋队，是中国特色社会主义事业的领导核心，代表中国先进生产力的发展要求，代表中国先进文化的前进方向，代表中国最广大人民的根本利益。党的最高理想和最终目标是实现共产主义。\n\n中国共产党以马克思列宁主义、毛泽东思想、邓小平理论、"三个代表"重要思想、科学发展观、习近平新时代中国特色社会主义思想作为自己的行动指南。\n\n## 第一章 党员\n\n第一条 年满十八岁的中国工人、农民、军人、知识分子和其他社会阶层的先进分子，承认党的纲领和章程，愿意参加党的一个组织并在其中积极工作、执行党的决议和按期交纳党费的，可以申请加入中国共产党。\n\n第二条 中国共产党党员是中国工人阶级的有共产主义觉悟的先锋战士。\n\n中国共产党党员必须全心全意为人民服务，不惜牺牲个人的一切，为实现共产主义奋斗终身。\n\n中国共产党党员永远是劳动人民的普通一员。除了法律和政策规定范围内的个人利益和工作职权以外，所有共产党员都不得谋求任何私利和特权。\n\n## 第二章 党的组织制度\n\n第十条 党是根据自己的纲领和章程，按照民主集中制组织起来的统一整体。党的民主集中制的基本原则是：\n\n（一）党员个人服从党的组织，少数服从多数，下级组织服从上级组织，全党各个组织和全体党员服从党的全国代表大会和中央委员会。\n\n（二）党的各级领导机关，除它们派出的代表机关和在非党组织中的党组外，都由选举产生。\n\n（三）党的最高领导机关，是党的全国代表大会和它所产生的中央委员会。党的地方各级领导机关，是党的地方各级代表大会和它们所产生的委员会。党的各级委员会向同级的代表大会负责并报告工作。\n\n（四）党的上级组织要经常听取下级组织和党员群众的意见，及时解决他们提出的问题。党的下级组织既要向上级组织请示和报告工作，又要独立负责地解决自己职责范围内的问题。上下级组织之间要互通情报、互相支持和互相监督。党的各级组织要按规定实行党务公开，使党员对党内事务有更多的了解和参与。\n\n（五）党的各级委员会实行集体领导和个人分工负责相结合的制度。凡属重大问题都要按照集体领导、民主集中、个别酝酿、会议决定的原则，由党的委员会集体讨论，作出决定；委员会成员要根据集体的决定和分工，切实履行自己的职责。\n\n（六）党禁止任何形式的个人崇拜。要保证党的领导人的活动处于党和人民的监督之下，同时维护一切代表党和人民利益的领导人的威信。' 
  },
  {
    id: 2,
    name: '党史学习重要事件汇总.docx',
    content: '# 党史学习重要事件汇总\n\n## 中国共产党成立（1921年）\n\n1921年7月23日，中国共产党第一次全国代表大会在上海召开，最后一天的会议转移到浙江嘉兴南湖的游船上举行。大会通过了中国共产党的第一个纲领和决议，选举产生了党的领导机构中央局，陈独秀为中央局书记。中国共产党的成立，是中国历史上开天辟地的大事变，中国革命的面貌从此焕然一新。\n\n## 南昌起义（1927年）\n\n1927年8月1日，周恩来、贺龙、叶挺、朱德、刘伯承等领导北伐军2万多人，在南昌举行武装起义，打响了武装反抗国民党反动派的第一枪，标志着中国共产党独立领导革命战争、创建人民军队和武装夺取政权的开端。\n\n## 秋收起义（1927年）\n\n1927年9月，毛泽东领导发动湘赣边界秋收起义，创建了中国第一个农村革命根据地——井冈山革命根据地，开辟了农村包围城市、武装夺取政权的正确革命道路。\n\n## 遵义会议（1935年）\n\n1935年1月，中共中央在贵州遵义召开政治局扩大会议，确立了毛泽东在党中央和红军的领导地位，挽救了党、挽救了红军、挽救了中国革命，是党的历史上一个生死攸关的转折点。\n\n## 抗日战争胜利（1945年）\n\n1945年8月15日，日本宣布无条件投降。中国人民抗日战争是近代以来中国人民反抗外敌入侵第一次取得完全胜利的民族解放战争，是世界反法西斯战争的重要组成部分。\n\n## 中华人民共和国成立（1949年）\n\n1949年10月1日，毛泽东在北京天安门城楼上庄严宣告中华人民共和国中央人民政府成立。中华人民共和国的成立，彻底结束了旧中国半殖民地半封建社会的历史，彻底结束了旧中国一盘散沙的局面，彻底废除了列强强加给中国的不平等条约和帝国主义在中国的一切特权，实现了中国从几千年封建专制政治向人民民主的伟大飞跃。' 
  },
  {
    id: 3,
    name: '习近平新时代中国特色社会主义思想核心内容.docx',
    content: '# 习近平新时代中国特色社会主义思想核心内容\n\n## 新时代坚持和发展中国特色社会主义的总目标、总任务、总体布局、战略布局\n\n总目标：实现社会主义现代化和中华民族伟大复兴\n\n总任务：实现第一个百年奋斗目标，开启实现第二个百年奋斗目标新征程\n\n总体布局：五位一体（经济建设、政治建设、文化建设、社会建设、生态文明建设）\n\n战略布局：四个全面（全面建设社会主义现代化国家、全面深化改革、全面依法治国、全面从严治党）\n\n## 新时代中国社会主要矛盾\n\n中国特色社会主义进入新时代，我国社会主要矛盾已经转化为人民日益增长的美好生活需要和不平衡不充分的发展之间的矛盾。\n\n## 新发展理念\n\n创新、协调、绿色、开放、共享的发展理念。\n\n## 全面建设社会主义现代化国家的战略安排\n\n第一个阶段，从二〇二〇年到二〇三五年，在全面建成小康社会的基础上，再奋斗十五年，基本实现社会主义现代化。\n\n第二个阶段，从二〇三五年到本世纪中叶，在基本实现现代化的基础上，再奋斗十五年，把我国建成富强民主文明和谐美丽的社会主义现代化强国。\n\n## 坚持和加强党的全面领导\n\n中国共产党是中国特色社会主义最本质的特征，是中国特色社会主义制度的最大优势。党政军民学，东西南北中，党是领导一切的。\n\n## 全面从严治党\n\n全面从严治党是新时代党的自我革命的伟大实践，开辟了百年大党自我革命的新境界。必须坚持和加强党的全面领导，坚持党要管党、全面从严治党，以加强党的长期执政能力建设、先进性和纯洁性建设为主线，以党的政治建设为统领，以坚定理想信念宗旨为根基，以调动全党积极性、主动性、创造性为着力点。\n\n## 推动构建人类命运共同体\n\n中国共产党是为中国人民谋幸福、为中华民族谋复兴的党，也是为人类进步事业而奋斗的党。中国共产党始终把为人类作出新的更大的贡献作为自己的使命。' 
  },
  {
    id: 4,
    name: '党风廉政建设重要文件汇编.docx',
    content: '# 党风廉政建设重要文件汇编\n\n## 中国共产党廉洁自律准则\n\n中国共产党全体党员和各级党员领导干部必须坚定共产主义理想和中国特色社会主义信念，必须坚持全心全意为人民服务根本宗旨，必须继承发扬党的优良传统和作风，必须自觉培养高尚道德情操，努力弘扬中华民族传统美德，廉洁自律，接受监督，永葆党的先进性和纯洁性。\n\n### 党员廉洁自律规范\n\n第一条 坚持公私分明，先公后私，克己奉公。\n\n第二条 坚持崇廉拒腐，清白做人，干净做事。\n\n第三条 坚持尚俭戒奢，艰苦朴素，勤俭节约。\n\n第四条 坚持吃苦在前，享受在后，甘于奉献。\n\n### 党员领导干部廉洁自律规范\n\n第五条 廉洁从政，自觉保持人民公仆本色。\n\n第六条 廉洁用权，自觉维护人民根本利益。\n\n第七条 廉洁修身，自觉提升思想道德境界。\n\n第八条 廉洁齐家，自觉带头树立良好家风。\n\n## 关于新形势下党内政治生活的若干准则\n\n办好中国的事情，关键在党，关键在党要管党、从严治党。党要管党必须从党内政治生活管起，从严治党必须从党内政治生活严起。\n\n新形势下加强和规范党内政治生活，必须以党章为根本遵循，坚持党的政治路线、思想路线、组织路线、群众路线，着力增强党内政治生活的政治性、时代性、原则性、战斗性，着力增强党自我净化、自我完善、自我革新、自我提高能力，着力提高党的领导水平和执政水平、增强拒腐防变和抵御风险能力，着力维护党中央权威、保证党的团结统一、保持党的先进性和纯洁性，努力在全党形成又有集中又有民主、又有纪律又有自由、又有统一意志又有个人心情舒畅生动活泼的政治局面。\n\n## 中国共产党纪律处分条例\n\n党的纪律是党的各级组织和全体党员必须遵守的行为规则。党组织和党员必须牢固树立政治意识、大局意识、核心意识、看齐意识，自觉遵守党章，严格执行和维护党的纪律，自觉接受党的纪律约束，模范遵守国家法律法规。\n\n对党员的纪律处分种类：\n\n（一）警告；\n（二）严重警告；\n（三）撤销党内职务；\n（四）留党察看；\n（五）开除党籍。\n\n党的纪律主要包括政治纪律、组织纪律、廉洁纪律、群众纪律、工作纪律、生活纪律。' 
  }
]

// 根据文件名获取模拟文件内容
const getFileContent = (fileName) => {
  const file = fileContents.find(item => item.name === fileName)
  if (!file) {
    return Promise.resolve('暂无该文件的预览内容')
  }
  return Promise.resolve(file.content)
}

// 模拟获取知识库
const fetchKnowledgeBaseDetail = () => {
  // 这里使用模拟数据，与KnowledgeBaseHome.vue中的静态样例数据对应
  const mockKnowledgeBases = [
    {
      id: 'kb_001',
      name: '中国共产党章程',
      description: '包含中国共产党的纲领、组织机构、党员权利义务等基本内容',
      createdAt: '2023-06-15 09:30',
      files: [
        { id: 1, name: '中国共产党章程全文.docx' }
      ]
    },
    {
      id: 'kb_002',
      name: '党史学习资料汇编',
      description: '汇总中国共产党从成立至今的重要历史事件、会议和人物',
      createdAt: '2023-07-20 14:45',
      files: [
        { id: 2, name: '党史学习重要事件汇总.docx' }
      ]
    },
    {
      id: 'kb_003',
      name: '习近平新时代中国特色社会主义思想',
      description: '深入解析习近平新时代中国特色社会主义思想的核心内容和实践要求',
      createdAt: '2023-08-10 11:20',
      files: [
        { id: 3, name: '习近平新时代中国特色社会主义思想核心内容.docx' }
      ]
    },
    {
      id: 'kb_004',
      name: '党风廉政建设学习手册',
      description: '包含党的纪律处分条例、廉洁自律准则等重要内容',
      createdAt: '2023-09-05 16:10',
      files: [
        { id: 4, name: '党风廉政建设重要文件汇编.docx' }
      ]
    }
  ]

  // 查找匹配的知识库
  const foundKnowledgeBase = mockKnowledgeBases.find(kb => kb.id === knowledgeBaseId)
  if (foundKnowledgeBase) {
    knowledgeBaseData.value = foundKnowledgeBase
    // 默认显示第一个文件
    if (foundKnowledgeBase.files.length > 0) {
      openFile(foundKnowledgeBase.files[0], 0)
    }
  } else {
    // 如果找不到匹配的知识库，显示第一个知识库作为默认值
    if (mockKnowledgeBases.length > 0) {
      knowledgeBaseData.value = mockKnowledgeBases[0]
      if (mockKnowledgeBases[0].files.length > 0) {
        openFile(mockKnowledgeBases[0].files[0], 0)
      }
    }
  }
}

// 简单的Markdown文本格式化
const formatText = (text) => {
  if (!text) return ''
  // 替换标题
  let formattedText = text
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    // 替换段落
    .replace(/^(?!<h[1-3]>)(.*$)/gm, '<p>$1</p>')
    // 替换空行
    .replace(/<p><\/p>/g, '')
    // 移除多余的换行符
    .replace(/\n/g, '')
    // 替换列表（这里简化处理，实际应用中可能需要更复杂的列表处理）不懂不懂
    .replace(/^(\s*-\s+)(.*$)/gm, '<ul><li>$2</li></ul>')
    .replace(/<\/ul>\s*<ul>/g, '')
  
  return formattedText
}

// 计算属性：格式化的内容
const markedContent = ref('')

// 打开文件
const openFile = (file, index) => {
  currentFileIndex.value = index
  currentFileName.value = file.name
  // 调用API获取文件内容
  getFileContent(file.name)
    .then(content => {
      currentFileContent.value = content
      markedContent.value = formatText(content)
    })
    .catch(error => {
      console.error('获取文件内容失败:', error)
      currentFileContent.value = '获取文件内容失败: ' + (error.message || '未知错误')
      markedContent.value = '<p>获取文件内容失败: ' + (error.message || '未知错误') + '</p>'
    })
}

// 返回知识库首页
const goBackToKnowledgeBaseHome = () => {
  router.push('/knowledge-base-home')
}

// 页面加载时获取数据
onMounted(() => {
  fetchKnowledgeBaseDetail()
  
  // 确保路由参数变化时重新加载数据
  const unwatch = route.params.id
  
  // 添加一些样式使页面看起来更美观
  const style = document.createElement('style')
  style.textContent = `
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background-color: #f5f5f5;
      color: #333;
    }
  `
  document.head.appendChild(style)
  
  return () => {
    document.head.removeChild(style)
  }
})
</script>

<template>
  <div class="knowledge-base-detail-container">
    <!-- 导航栏 -->
    <header class="header">
      <div class="logo">智慧党建</div>
      <nav class="nav">
        <button class="nav-button" @click="goBackToKnowledgeBaseHome">返回</button>
      </nav>
      <div class="search-bar">
        <input
          placeholder="搜索内容..."
          class="search-input"
        >
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 侧边栏 - 文件列表 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h3 class="sidebar-title">文件列表</h3>
        </div>
        <div class="file-list">
          <div
            v-for="(file, index) in knowledgeBaseData.files"
            :key="file.id"
            class="file-item"
            :class="{ active: currentFileIndex === index }"
            @click="openFile(file, index)"
          >
            <div class="file-icon">📄</div>
            <div class="file-name">{{ file.name }}</div>
          </div>
        </div>
      </aside>

      <!-- 内容区域 -->
      <div class="content-area">
        <!-- 知识库信息 -->
        <div class="knowledge-base-info">
          <h2 class="knowledge-base-name">{{ knowledgeBaseData.name }}</h2>
          <p class="knowledge-base-description">{{ knowledgeBaseData.description }}</p>
          <p class="knowledge-base-createdAt">创建时间：{{ knowledgeBaseData.createdAt }}</p>
        </div>

        <!-- 文件内容 -->
        <div class="file-content">
          <div class="file-header">
            <h3 class="current-file-name">{{ currentFileName }}</h3>
          </div>
          <div class="content-wrapper">
            <div class="markdown-content" v-html="markedContent"></div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.knowledge-base-detail-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #fdf2e9 0%, #fff 100%);
}

/* 导航栏 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 68px;
  background: linear-gradient(90deg, #8b0000 0%, #cd5c5c 100%);
  border-bottom: 3px solid #ffd700;
  box-shadow: 0 4px 12px rgba(139, 0, 0, 0.3);
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  background: linear-gradient(135deg, #ffd700 0%, #ffed4a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-button {
  padding: 8px 16px;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
  color: #8b0000;
  border: 1px solid rgba(255, 215, 0, 0.6);
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  font-weight: 500;
}

.nav-button:hover {
  background: linear-gradient(135deg, #fff 0%, #ffebcd 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  border-color: #ffd700;
}

.search-bar {
  width: 300px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid rgba(255, 215, 0, 0.5);
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
  background-color: rgba(255, 255, 255, 0.9);
}

.search-input:focus {
  outline: none;
  border-color: #8b0000;
  box-shadow: 0 0 0 3px rgba(139, 0, 0, 0.1);
}

/* 主内容区 */
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
  background: linear-gradient(135deg, #fdf2e9 0%, #fff 100%);
}

/* 侧边栏 */
.sidebar {
  width: 300px;
  background: linear-gradient(180deg, #fff 0%, #fdf2e9 100%);
  border-right: 2px solid #ffd700;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(139, 0, 0, 0.1);
  position: relative;
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 6px;
  background: linear-gradient(90deg, #8b0000 0%, #cd5c5c 100%);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.3);
  position: relative;
}

.sidebar-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20px;
  width: calc(100% - 40px);
  height: 3px;
  background: linear-gradient(90deg, #8b0000 0%, transparent 100%);
}

.sidebar-title {
  font-size: 18px;
  font-weight: bold;
  color: #8b0000;
  margin: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.file-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 5px;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  position: relative;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.file-item:hover {
  background: linear-gradient(135deg, #fff 0%, #ffebcd 100%);
  transform: translateX(3px);
  box-shadow: 0 3px 8px rgba(139, 0, 0, 0.1);
}

.file-item.active {
  background: linear-gradient(135deg, rgba(139, 0, 0, 0.05) 0%, rgba(205, 92, 92, 0.03) 100%);
  border-color: #8b0000;
  box-shadow: 0 2px 6px rgba(139, 0, 0, 0.15);
}

.file-item.active::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 8px;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: linear-gradient(180deg, #ffd700 0%, #ffed4a 100%);
  border-radius: 2px;
}

.file-icon {
  font-size: 18px;
  margin-right: 10px;
  color: #8b0000;
  transition: all 0.3s;
}

.file-item:hover .file-icon {
  color: #cd5c5c;
  transform: scale(1.1);
}

.file-item.active .file-icon {
  color: #8b0000;
  transform: scale(1.1);
}

.file-name {
  flex: 1;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.file-item.active .file-name {
  color: #8b0000;
}

/* 内容区域 */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: linear-gradient(135deg, #fdf2e9 0%, #fff 100%);
}

/* 知识库信息 */
.knowledge-base-info {
  padding: 20px;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
  border-bottom: 2px solid #ffd700;
  box-shadow: 0 2px 8px rgba(139, 0, 0, 0.05);
  position: relative;
}

.knowledge-base-info::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #8b0000 0%, #cd5c5c 100%);
}

.knowledge-base-name {
  font-size: 24px;
  font-weight: bold;
  color: #8b0000;
  margin: 0 0 10px 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.knowledge-base-description {
  font-size: 16px;
  color: #666;
  margin: 0 0 10px 0;
  line-height: 1.6;
}

.knowledge-base-createdAt {
  font-size: 14px;
  color: #999;
  margin: 0;
  font-style: italic;
}

/* 文件内容 */
.file-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 5%);
}

.file-header {
  padding: 20px;
  background: linear-gradient(90deg, rgba(139, 0, 0, 0.05) 0%, transparent 100%);
  border: 2px solid rgba(255, 215, 0, 0.3);
  border-bottom: none;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.current-file-name {
  font-size: 18px;
  font-weight: bold;
  color: #8b0000;
  margin: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05);
}

.content-wrapper {
  flex: 1;
  padding: 0;
  overflow-y: auto;
  background-color: transparent;
  border: 2px solid rgba(255, 215, 0, 0.3);
  border-top: none;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}

.markdown-content {
  max-width: 100%;
  width: 100%;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
  line-height: 1.8;
  font-size: 16px;
  color: #333;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  position: relative;
}

/* 为markdown内容添加党建主题的装饰元素 */
.markdown-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, #8b0000 0%, #cd5c5c 100%);
  opacity: 0.8;
}

/* Markdown标题样式调整 */
.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  color: #8b0000;
  font-weight: bold;
  margin-top: 1.5em;
  margin-bottom: 0.8em;
  position: relative;
}

.markdown-content h1::after,
.markdown-content h2::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -5px;
  width: 100px;
  height: 3px;
  background: linear-gradient(90deg, #ffd700 0%, #ffed4a 100%);
}

/* Markdown段落样式 */
.markdown-content p {
  margin-bottom: 1.2em;
  text-align: justify;
}

/* Markdown链接样式 */
.markdown-content a {
  color: #8b0000;
  text-decoration: none;
  border-bottom: 1px solid rgba(139, 0, 0, 0.3);
  transition: all 0.3s;
}

.markdown-content a:hover {
  color: #cd5c5c;
  border-bottom-color: #ffd700;
  text-shadow: 0 0 2px rgba(255, 215, 0, 0.2);
}

/* Markdown列表样式 */
.markdown-content ul,
.markdown-content ol {
  padding-left: 1.5em;
  margin-bottom: 1.2em;
}

.markdown-content li {
  margin-bottom: 0.5em;
  position: relative;
}

/* Markdown引用样式 */
.markdown-content blockquote {
  border-left: 4px solid #8b0000;
  padding-left: 1em;
  margin-left: 0;
  margin-right: 0;
  font-style: italic;
  color: #666;
  background-color: rgba(139, 0, 0, 0.05);
  padding: 1em;
  border-radius: 0 4px 4px 0;
}

/* Markdown代码块样式 */
.markdown-content pre {
  background-color: rgba(139, 0, 0, 0.05);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 4px;
  padding: 1em;
  overflow-x: auto;
  margin-bottom: 1.2em;
}

.markdown-content code {
  background-color: rgba(139, 0, 0, 0.05);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.9em;
}

/* 确保markdown-content有正确的padding */
.markdown-content {
  padding: 30px;
}

/* 删除重复的段落样式，保留我们之前定义的样式 */
.markdown-content h1 {
  font-size: 24px;
  margin-top: 1.5em;
  margin-bottom: 0.8em;
  color: #8b0000;
  font-weight: bold;
  position: relative;
}

.markdown-content h1::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -5px;
  width: 100px;
  height: 3px;
  background: linear-gradient(90deg, #ffd700 0%, #ffed4a 100%);
}

/* 修复所有标题样式，确保与党建主题一致 */
.markdown-content h2 {
  font-size: 20px;
  margin-top: 1.5em;
  margin-bottom: 0.8em;
  color: #8b0000;
  font-weight: bold;
  position: relative;
}

.markdown-content h2::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -5px;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #ffd700 0%, #ffed4a 100%);
}

.markdown-content h3 {
  font-size: 18px;
  margin-top: 1.2em;
  margin-bottom: 0.6em;
  color: #8b0000;
  font-weight: bold;
}

.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  color: #8b0000;
  font-weight: bold;
}

/* 确保段落样式统一 */
.markdown-content p {
  margin-bottom: 1.2em;
  text-align: justify;
  line-height: 1.8;
  color: #333;
}

/* 列表样式统一 */
.markdown-content ul, 
.markdown-content ol {
  margin-bottom: 1.2em;
  padding-left: 1.5em;
  color: #333;
}

.markdown-content li {
  margin-bottom: 0.5em;
  position: relative;
}

/* 滚动条样式 - 党建主题风格 */
.file-list::-webkit-scrollbar,
.content-wrapper::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.file-list::-webkit-scrollbar-track,
.content-wrapper::-webkit-scrollbar-track {
  background: #fdf2e9;
  border-radius: 4px;
}

.file-list::-webkit-scrollbar-thumb,
.content-wrapper::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #cd5c5c 0%, #8b0000 100%);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.file-list::-webkit-scrollbar-thumb:hover,
.content-wrapper::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #8b0000 0%, #6b0000 100%);
  border-color: rgba(255, 255, 255, 0.5);
}
</style>