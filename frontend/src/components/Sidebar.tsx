import { VStack, IconButton, Box, Tooltip } from '@chakra-ui/react'
import { HiViewGrid, HiChat } from 'react-icons/hi'

interface SidebarProps {
  activeTab: 'marketplace' | 'chat'
  onTabChange: (tab: 'marketplace' | 'chat') => void
}

const Sidebar = ({ activeTab, onTabChange }: SidebarProps) => {
  return (
    <Box 
      w="60px" 
      bg="gray.50" 
      borderRight="1px" 
      borderColor="gray.200" 
      py={4}
      display="flex"
      flexDirection="column"
      alignItems="center"
    >
      <VStack spacing={1} width="100%">
        <Tooltip label="Marketplace" placement="right" hasArrow>
          <IconButton
            aria-label="Marketplace"
            icon={<HiViewGrid size={20} />}
            variant="ghost"
            size="lg"
            width="48px"
            height="48px"
            borderRadius="md"
            colorScheme={activeTab === 'marketplace' ? 'blue' : 'gray'}
            bg={activeTab === 'marketplace' ? 'blue.100' : 'transparent'}
            color={activeTab === 'marketplace' ? 'blue.600' : 'gray.600'}
            _hover={{
              bg: activeTab === 'marketplace' ? 'blue.200' : 'gray.100',
              color: activeTab === 'marketplace' ? 'blue.700' : 'gray.700'
            }}
            _active={{
              bg: activeTab === 'marketplace' ? 'blue.200' : 'gray.200'
            }}
            onClick={() => onTabChange('marketplace')}
          />
        </Tooltip>
        
        <Tooltip label="Chat" placement="right" hasArrow>
          <IconButton
            aria-label="Chat"
            icon={<HiChat size={20} />}
            variant="ghost"
            size="lg"
            width="48px"
            height="48px"
            borderRadius="md"
            colorScheme={activeTab === 'chat' ? 'blue' : 'gray'}
            bg={activeTab === 'chat' ? 'blue.100' : 'transparent'}
            color={activeTab === 'chat' ? 'blue.600' : 'gray.600'}
            _hover={{
              bg: activeTab === 'chat' ? 'blue.200' : 'gray.100',
              color: activeTab === 'chat' ? 'blue.700' : 'gray.700'
            }}
            _active={{
              bg: activeTab === 'chat' ? 'blue.200' : 'gray.200'
            }}
            onClick={() => onTabChange('chat')}
          />
        </Tooltip>
      </VStack>
    </Box>
  )
}

export default Sidebar