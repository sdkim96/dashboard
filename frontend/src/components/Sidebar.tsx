import { VStack, IconButton, Box, Tooltip } from '@chakra-ui/react'
import { HiViewGrid, HiChat, HiArchive } from 'react-icons/hi'

import type { ActiveTab } from '../types/type'

interface SidebarProps {
  activeTab: ActiveTab
  onTabChange: (tab: ActiveTab) => void
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
        <Tooltip label="Recommendations" placement="right" hasArrow>
          <IconButton
            aria-label="Recommendations"
            icon={<HiArchive size={20} />}
            variant="ghost"
            size="lg"
            width="48px"
            height="48px"
            borderRadius="md"
            colorScheme={activeTab === 'recommendations' ? 'blue' : 'gray'}
            bg={activeTab === 'recommendations' ? 'blue.100' : 'transparent'}
            color={activeTab === 'recommendations' ? 'blue.600' : 'gray.600'}
            _hover={{
              bg: activeTab === 'recommendations' ? 'blue.200' : 'gray.100',
              color: activeTab === 'recommendations' ? 'blue.700' : 'gray.700'
            }}
            _active={{
              bg: activeTab === 'recommendations' ? 'blue.200' : 'gray.200'
            }}
            onClick={() => onTabChange('recommendations')}
          />
        </Tooltip>

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
        
        {/* <Tooltip label="Chat" placement="right" hasArrow>
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
        </Tooltip> */}
      </VStack>
    </Box>
  )
}

export default Sidebar