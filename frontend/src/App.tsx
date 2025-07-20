import { useState } from 'react'
import { Box } from '@chakra-ui/react'
import Sidebar from './components/Sidebar'
import MarketplaceView from './views/MarketplaceView'
import ChatView from './views/ChatView'

function App() {
  const [activeTab, setActiveTab] = useState<'marketplace' | 'chat'>('marketplace')

  return (
    <Box display="flex" h="100vh" bg="gray.50">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <Box flex="1">
        {activeTab === 'marketplace' ? <MarketplaceView /> : <ChatView />}
      </Box>
    </Box>
  )
}

export default App