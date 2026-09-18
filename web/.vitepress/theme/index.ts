import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import EntityExplorer from './components/EntityExplorer.vue'
import EvidenceCard from './components/EvidenceCard.vue'
import ReportSummary from './components/ReportSummary.vue'
import StatusBadge from './components/StatusBadge.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('EntityExplorer', EntityExplorer)
    app.component('EvidenceCard', EvidenceCard)
    app.component('ReportSummary', ReportSummary)
    app.component('StatusBadge', StatusBadge)
  }
} satisfies Theme
