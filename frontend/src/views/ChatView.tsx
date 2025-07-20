import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Flex,
  IconButton,
  Text,
  Textarea,
  Button,
  VStack,
  HStack,
  Avatar,
  Divider,
  useDisclosure,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useBreakpointValue,
  Tooltip,
  Badge
} from '@chakra-ui/react';
import { 
  HiMenu,
  HiPlus,
  HiChevronLeft,
  HiChevronRight,
  HiChat,
  HiCog,
  HiPencil,
  HiTrash
} from 'react-icons/hi';


// TypeScript 타입 정의
interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Conversation {
  id: number;
  title: string;
  lastMessage: string;
  active: boolean;
}

interface SidebarContentProps {
  conversations: Conversation[];
  onNewChat: () => void;
  onSelectConversation: (id: number) => void;
  onEditConversation: (id: number) => void;
  onDeleteConversation: (id: number) => void;
}

const ChatInterface: React.FC = () => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: 'assistant',
      content: 'Hello! I\'m your AI assistant. How can I help you today?',
      timestamp: new Date()
    }
  ]);
  const [conversations, setConversations] = useState<Conversation[]>([
    { id: 1, title: 'General Chat', lastMessage: 'Hello! How can I help...', active: true },
    { id: 2, title: 'Code Review Help', lastMessage: 'Can you review this...', active: false },
    { id: 3, title: 'Writing Assistance', lastMessage: 'I need help with...', active: false },
  ]);

  const { isOpen, onOpen, onClose } = useDisclosure();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isMobile = useBreakpointValue({ base: true, md: false });

  const scrollToBottom = (): void => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (): void => {
    if (!message.trim()) return;

    const newUserMessage: Message = {
      id: messages.length + 1,
      role: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newUserMessage]);
    setMessage('');

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: messages.length + 2,
        role: 'assistant',
        content: 'I understand your message. Let me help you with that...',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewChat = (): void => {
    console.log('New chat');
  };

  const handleSelectConversation = (id: number): void => {
    setConversations(prev => 
      prev.map(conv => ({ ...conv, active: conv.id === id }))
    );
  };

  const handleEditConversation = (id: number): void => {
    console.log('Edit conversation', id);
  };

  const handleDeleteConversation = (id: number): void => {
    console.log('Delete conversation', id);
  };

  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    setMessage(e.target.value);
  };

  const SidebarContent: React.FC<SidebarContentProps> = ({ 
    conversations, 
    onNewChat, 
    onSelectConversation, 
    onEditConversation, 
    onDeleteConversation 
  }) => (
    <VStack h="100%" spacing={0} align="stretch">
      {/* Header */}
      <Flex p={4} align="center" justify="space-between" borderBottom="1px" borderColor="gray.200">
        <Text fontSize="lg" fontWeight="bold">Chats</Text>
        <Tooltip label="New Chat">
          <IconButton
            icon={<HiPlus />}
            size="sm"
            variant="ghost"
            aria-label="New Chat"
            onClick={onNewChat}
          />
        </Tooltip>
      </Flex>

      {/* Conversations List */}
      <VStack flex={1} spacing={1} p={2} align="stretch" overflowY="auto">
        {conversations.map((conv: Conversation) => (
          <Box
            key={conv.id}
            p={3}
            borderRadius="md"
            bg={conv.active ? "blue.50" : "transparent"}
            borderLeft={conv.active ? "3px solid" : "3px solid transparent"}
            borderColor="blue.500"
            cursor="pointer"
            _hover={{ bg: "gray.50" }}
            position="relative"
            role="group"
            onClick={() => onSelectConversation(conv.id)}
          >
            <HStack justify="space-between" align="start">
              <VStack align="start" spacing={1} flex={1} minW={0}>
                <Text fontSize="sm" fontWeight={conv.active ? "semibold" : "normal"} noOfLines={1}>
                  {conv.title}
                </Text>
                <Text fontSize="xs" color="gray.500" noOfLines={2}>
                  {conv.lastMessage}
                </Text>
              </VStack>
              
              <HStack 
                spacing={1} 
                opacity={0} 
                _groupHover={{ opacity: 1 }}
                transition="opacity 0.2s"
                onClick={(e: React.MouseEvent) => e.stopPropagation()}
              >
                <IconButton
                  icon={<HiPencil />}
                  size="xs"
                  variant="ghost"
                  aria-label="Edit"
                  onClick={() => onEditConversation(conv.id)}
                />
                <IconButton
                  icon={<HiTrash />}
                  size="xs"
                  variant="ghost"
                  aria-label="Delete"
                  onClick={() => onDeleteConversation(conv.id)}
                />
              </HStack>
            </HStack>
          </Box>
        ))}
      </VStack>

      <Divider />

      {/* Settings */}
      <Box p={4}>
        <HStack spacing={3} cursor="pointer" _hover={{ bg: "gray.50" }} p={2} borderRadius="md">
          <HiCog />
          <Text fontSize="sm">Settings</Text>
        </HStack>
      </Box>
    </VStack>
  );

  const toggleSidebar = (): void => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <Flex h="100vh" bg="gray.50">
      {/* Desktop Sidebar */}
      {!isMobile && (
        <Box
          w={isSidebarCollapsed ? "60px" : "280px"}
          bg="white"
          borderRight="1px"
          borderColor="gray.200"
          transition="width 0.3s ease"
          position="relative"
        >
          {/* Collapse Button */}
          <IconButton
            icon={isSidebarCollapsed ? <HiChevronRight /> : <HiChevronLeft />}
            size="sm"
            position="absolute"
            right="-12px"
            top="20px"
            zIndex={10}
            bg="white"
            border="1px"
            borderColor="gray.200"
            borderRadius="full"
            _hover={{ bg: "gray.50" }}
            onClick={toggleSidebar}
            aria-label="Toggle Sidebar"
          />

          {isSidebarCollapsed ? (
            <VStack p={3} spacing={4}>
              <Tooltip label="New Chat" placement="right">
                <IconButton
                  icon={<HiPlus />}
                  size="md"
                  variant="ghost"
                  aria-label="New Chat"
                  onClick={handleNewChat}
                />
              </Tooltip>
              <Tooltip label="Chats" placement="right">
                <IconButton
                  icon={<HiChat />}
                  size="md"
                  variant="ghost"
                  aria-label="Chats"
                />
              </Tooltip>
              <Tooltip label="Settings" placement="right">
                <IconButton
                  icon={<HiCog />}
                  size="md"
                  variant="ghost"
                  aria-label="Settings"
                />
              </Tooltip>
            </VStack>
          ) : (
            <SidebarContent 
              conversations={conversations}
              onNewChat={handleNewChat}
              onSelectConversation={handleSelectConversation}
              onEditConversation={handleEditConversation}
              onDeleteConversation={handleDeleteConversation}
            />
          )}
        </Box>
      )}

      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="sm">
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader borderBottom="1px" borderColor="gray.200">
            Chats
          </DrawerHeader>
          <DrawerBody p={0}>
            <SidebarContent 
              conversations={conversations}
              onNewChat={handleNewChat}
              onSelectConversation={handleSelectConversation}
              onEditConversation={handleEditConversation}
              onDeleteConversation={handleDeleteConversation}
            />
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Main Chat Area */}
      <Flex flex={1} direction="column" maxW="100%">
        {/* Header */}
        <Flex
          h="60px"
          px={6}
          align="center"
          justify="space-between"
          bg="white"
          borderBottom="1px"
          borderColor="gray.200"
        >
          {isMobile && (
            <IconButton
              icon={<HiMenu />}
              variant="ghost"
              onClick={onOpen}
              aria-label="Open Menu"
            />
          )}
          
          <Text fontSize="lg" fontWeight="semibold" flex={1} textAlign={isMobile ? "center" : "left"}>
            General Chat
          </Text>
          
          <Badge colorScheme="green" variant="subtle">
            GPT-4
          </Badge>
        </Flex>

        {/* Messages Area */}
        <Box flex={1} overflowY="auto" bg="white">
          <VStack spacing={0} align="stretch" maxW="3xl" mx="auto" py={6}>
            {messages.map((msg: Message) => (
              <Box key={msg.id} px={6} py={4}>
                <HStack align="start" spacing={4}>
                  <Avatar
                    size="sm"
                    name={msg.role === 'user' ? 'User' : 'Assistant'}
                    bg={msg.role === 'user' ? 'blue.500' : 'green.500'}
                    color="white"
                  />
                  
                  <VStack align="start" flex={1} spacing={2}>
                    <Text fontSize="sm" fontWeight="semibold" color="gray.600">
                      {msg.role === 'user' ? 'You' : 'Assistant'}
                    </Text>
                    <Text fontSize="md" lineHeight="1.6" whiteSpace="pre-wrap">
                      {msg.content}
                    </Text>
                  </VStack>
                </HStack>
              </Box>
            ))}
            <div ref={messagesEndRef} />
          </VStack>
        </Box>

        {/* Input Area */}
        <Box bg="white" borderTop="1px" borderColor="gray.200" p={4}>
          <Box maxW="3xl" mx="auto">
            <HStack spacing={3}>
              <Box flex={1} position="relative">
                <Textarea
                  ref={textareaRef}
                  value={message}
                  onChange={handleMessageChange}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  resize="none"
                  minH="44px"
                  maxH="200px"
                  border="1px"
                  borderColor="gray.300"
                  borderRadius="lg"
                  _focus={{
                    borderColor: "blue.500",
                    boxShadow: "0 0 0 1px blue.500"
                  }}
                  pr="50px"
                />
                <IconButton
                  icon={<Text fontSize="lg">→</Text>}
                  size="sm"
                  position="absolute"
                  right="8px"
                  bottom="8px"
                  colorScheme="blue"
                  borderRadius="md"
                  isDisabled={!message.trim()}
                  onClick={handleSendMessage}
                  aria-label="Send Message"
                />
              </Box>
            </HStack>
            
            <Text fontSize="xs" color="gray.500" textAlign="center" mt={2}>
              Press Enter to send, Shift+Enter for new line
            </Text>
          </Box>
        </Box>
      </Flex>
    </Flex>
  );
};

export default ChatInterface;