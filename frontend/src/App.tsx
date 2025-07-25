import { useState } from 'react'
import { Box } from '@chakra-ui/react'

import type { ActiveTab } from './types/activeTabs'

import Sidebar from './components/Sidebar'

import MarketplaceView from './views/MarketplaceView'
import RecommendationsView from './views/RecommendationsView'
import ChatView from './views/ChatView'

function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('recommendations')

  return (
    <Box display="flex" h="100vh" bg="gray.50">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <Box flex="1">
        {(() => {
          switch(activeTab) {
            case 'marketplace':
              return <MarketplaceView />
            case 'chat':
              return <ChatView />
            case 'recommendations':
              return <RecommendationsView />
            default:
              return <Box>Unknown Tab</Box>
          }
        })()}
      </Box>
    </Box>
  )
}

export default App