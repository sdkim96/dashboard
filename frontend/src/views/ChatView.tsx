import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  IconButton,
  Text,
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
  Badge,
  useToast,
  Skeleton,
} from '@chakra-ui/react';
import { 
  HiPlus,
  HiChevronLeft,
  HiChevronRight,
  HiChat,
  HiCog,
  HiPencil,
  HiTrash
} from 'react-icons/hi';

// API 및 타입 import
import {
  getConversationsApiV1ConversationsGet,
  getConversationApiV1ConversationsConversationIdGet,
  getMeApiV1UserGet,
  type ConversationMaster,
  type MessageResponse,
  type LlmModel,
  type User,
  type Agent
} from '../client';

// 컴포넌트 import
import ConversationWindow from './ConversationWindow';

// 사이드바 컴포넌트 Props
interface SidebarContentProps {
  conversations: ConversationMaster[];
  selectedConversationId: string | null;
  loading: boolean;
  subscribedAgents: Agent[];
  selectedAgent: Agent | null;
  userInfo: User | null;
  onNewChat: () => void;
  onSelectConversation: (conversationId: string) => void;
  onEditConversation: (conversationId: string) => void;
  onDeleteConversation: (conversationId: string) => void;
  onSelectAgent: (agent: Agent) => void;
}

const ChatView: React.FC = () => {
  // States
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');
  const [conversations, setConversations] = useState<ConversationMaster[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [messagesLoading, setMessagesLoading] = useState<boolean>(false);
  const [sendingMessage, setSendingMessage] = useState<boolean>(false);
  
  // 사용자 정보 관련 state
  const [userInfo, setUserInfo] = useState<User | null>(null);
  const [availableModels, setAvailableModels] = useState<LlmModel[]>([]);
  const [subscribedAgents, setSubscribedAgents] = useState<Agent[]>([]);
  const [selectedModel, setSelectedModel] = useState<LlmModel | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  // Refs and hooks
  const { isOpen, onOpen, onClose } = useDisclosure();
  const isMobile = useBreakpointValue({ base: true, md: false });
  const toast = useToast();

  // Effects
  useEffect(() => {
    Promise.all([
      fetchUserInfo(),
      fetchConversations()
    ]);
  }, []);

  useEffect(() => {
    if (selectedConversationId) {
      fetchConversationDetails(selectedConversationId);
    }
  }, [selectedConversationId]);

  // Utility functions
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  // API functions
  const fetchUserInfo = async (): Promise<void> => {
    try {
      const response = await getMeApiV1UserGet();
      
      if (response.data) {
        setUserInfo(response.data.user);
        
        if (response.data.llms) {
          setAvailableModels(response.data.llms);
          if (response.data.llms.length > 0) {
            setSelectedModel(response.data.llms[0]);
          }
        }
        
        if (response.data.agents) {
          setSubscribedAgents(response.data.agents);
          if (response.data.agents.length > 0) {
            setSelectedAgent(response.data.agents[0]);
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      toast({
        title: 'Error',
        description: 'Failed to load user information',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const fetchConversations = async (): Promise<void> => {
    setLoading(true);
    try {
      const response = await getConversationsApiV1ConversationsGet();
      
      if (response.data && response.data.conversations) {
        setConversations(response.data.conversations);
        
        if (response.data.conversations.length > 0 && !selectedConversationId) {
          setSelectedConversationId(response.data.conversations[0].conversation_id);
        }
      }
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
      toast({
        title: 'Error',
        description: 'Failed to load conversations',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchConversationDetails = async (conversationId: string): Promise<void> => {
    setMessagesLoading(true);
    try {
      const response = await getConversationApiV1ConversationsConversationIdGet({
        path: { conversation_id: conversationId }
      });
      
      if (response.data && response.data.messages) {
        setMessages(response.data.messages);
      } else {
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to fetch conversation details:', error);
      toast({
        title: 'Error',
        description: 'Failed to load conversation details',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setMessagesLoading(false);
    }
  };

  // Event handlers
  const handleSendMessage = (): void => {
    if (!message.trim() || !selectedConversationId) return;

    setSendingMessage(true);
    
    const newUserMessage: MessageResponse = {
      message_id: `msg-${Date.now()}`,
      role: 'user',
      content: {
        type: 'text',
        parts: [message]
      },
      llm: null,
      agent_id: selectedAgent?.agent_id,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, newUserMessage]);
    setMessage('');

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: MessageResponse = {
        message_id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: {
          type: 'text',
          parts: [`I understand your message. Let me help you with that using ${selectedModel?.name || 'the selected model'}...`]
        },
        llm: selectedModel || {
          issuer: 'openai',
          deployment_id: 'gpt-4',
          name: 'GPT-4',
          description: 'GPT-4 Model',
          icon_link: null
        },
        agent_id: selectedAgent?.agent_id || null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, aiResponse]);
      setSendingMessage(false);
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

  const handleSelectConversation = (conversationId: string): void => {
    setSelectedConversationId(conversationId);
  };

  const handleEditConversation = (conversationId: string): void => {
    console.log('Edit conversation', conversationId);
  };

  const handleDeleteConversation = (conversationId: string): void => {
    console.log('Delete conversation', conversationId);
  };

  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    setMessage(e.target.value);
  };

  const toggleSidebar = (): void => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  const handleSelectAgent = (agent: Agent): void => {
    setSelectedAgent(agent);
  };

  const onSelectModel = (model: LlmModel): void => {
    setSelectedModel(model);
  };

  // 현재 선택된 대화 찾기
  const selectedConversation = conversations.find(
    conv => conv.conversation_id === selectedConversationId
  );

  // 사이드바 컨텐츠 컴포넌트
  const SidebarContent: React.FC<SidebarContentProps> = ({ 
    conversations, 
    selectedConversationId,
    loading,
    subscribedAgents,
    selectedAgent,
    userInfo,
    onNewChat, 
    onSelectConversation, 
    onEditConversation, 
    onDeleteConversation,
    onSelectAgent
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
        {/* 구독한 에이전트들 표시 */}
        {subscribedAgents.length > 0 && (
          <Box mb={4}>
            <Text fontSize="xs" fontWeight="semibold" color="gray.600" mb={2} px={1}>
              SUBSCRIBED AGENTS
            </Text>
            <VStack spacing={1}>
              {subscribedAgents.map((agent) => (
                <Box
                  key={`${agent.agent_id}-${agent.agent_version}`}
                  p={3}
                  borderRadius="md"
                  bg={selectedAgent?.agent_id === agent.agent_id && selectedAgent?.agent_version === agent.agent_version ? "green.50" : "transparent"}
                  border={selectedAgent?.agent_id === agent.agent_id && selectedAgent?.agent_version === agent.agent_version ? "2px solid" : "1px solid"}
                  borderColor={selectedAgent?.agent_id === agent.agent_id && selectedAgent?.agent_version === agent.agent_version ? "green.500" : "gray.200"}
                  cursor="pointer"
                  _hover={{ bg: "gray.50", borderColor: "green.300" }}
                  onClick={() => onSelectAgent(agent)}
                  w="100%"
                  transition="all 0.2s"
                >
                  <HStack spacing={3}>
                    <Avatar
                      size="sm"
                      name={agent.name}
                      src={agent.icon_link || undefined}
                      bg="green.500"
                    />
                    <VStack align="start" spacing={0} flex={1}>
                      <Text fontSize="sm" fontWeight="medium" noOfLines={1}>
                        {agent.name}
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        v{agent.agent_version}
                      </Text>
                    </VStack>
                    {selectedAgent?.agent_id === agent.agent_id && selectedAgent?.agent_version === agent.agent_version && (
                      <Badge size="sm" colorScheme="green" variant="solid">
                        ✓
                      </Badge>
                    )}
                  </HStack>
                </Box>
              ))}
            </VStack>
          </Box>
        )}

        <Divider mb={2} />
        
        {/* 대화 목록 */}
        <Text fontSize="xs" fontWeight="semibold" color="gray.600" mb={2} px={1}>
          CONVERSATIONS
        </Text>
        {loading ? (
          Array.from({ length: 5 }).map((_, index) => (
            <Box key={index} p={3} borderRadius="md">
              <VStack align="start" spacing={2}>
                <Skeleton height="16px" width="70%" />
                <Skeleton height="12px" width="90%" />
              </VStack>
            </Box>
          ))
        ) : conversations.length > 0 ? (
          conversations.map((conv: ConversationMaster) => (
            <Box
              key={conv.conversation_id}
              p={3}
              borderRadius="md"
              bg={selectedConversationId === conv.conversation_id ? "blue.50" : "transparent"}
              borderLeft={selectedConversationId === conv.conversation_id ? "3px solid" : "3px solid transparent"}
              borderColor="blue.500"
              cursor="pointer"
              _hover={{ bg: "gray.50" }}
              position="relative"
              role="group"
              onClick={() => onSelectConversation(conv.conversation_id)}
            >
              <HStack justify="space-between" align="start">
                <VStack align="start" spacing={1} flex={1} minW={0}>
                  <HStack spacing={2}>
                    {conv.icon && <Text fontSize="sm">{conv.icon}</Text>}
                    <Text 
                      fontSize="sm" 
                      fontWeight={selectedConversationId === conv.conversation_id ? "semibold" : "normal"} 
                      noOfLines={1}
                    >
                      {conv.title}
                    </Text>
                  </HStack>
                  <Text fontSize="xs" color="gray.500">
                    {formatDate(conv.updated_at)}
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
                    onClick={() => onEditConversation(conv.conversation_id)}
                  />
                  <IconButton
                    icon={<HiTrash />}
                    size="xs"
                    variant="ghost"
                    aria-label="Delete"
                    onClick={() => onDeleteConversation(conv.conversation_id)}
                  />
                </HStack>
              </HStack>
            </Box>
          ))
        ) : (
          <Box p={4} textAlign="center">
            <Text fontSize="sm" color="gray.500">
              No conversations yet
            </Text>
          </Box>
        )}
      </VStack>

      <Divider />

      {/* Settings */}
      <Box p={4}>
        <VStack spacing={3}>
          {/* 사용자 정보 표시 */}
          {userInfo && (
            <HStack 
              spacing={3} 
              cursor="pointer" 
              _hover={{ bg: "gray.50" }} 
              p={2} 
              borderRadius="md"
              w="100%"
            >
              <Avatar 
                size="sm" 
                name={userInfo.username}
                src={userInfo.icon_link || undefined}
                bg="blue.500"
              />
              <VStack align="start" spacing={0} flex={1}>
                <Text fontSize="sm" fontWeight="semibold" noOfLines={1}>
                  {userInfo.username}
                </Text>
                {userInfo.email && (
                  <Text fontSize="xs" color="gray.500" noOfLines={1}>
                    {userInfo.email}
                  </Text>
                )}
              </VStack>
              {userInfo.is_superuser && (
                <Badge size="sm" colorScheme="purple" variant="subtle">
                  Admin
                </Badge>
              )}
            </HStack>
          )}
          
          <Divider />
          
          <HStack spacing={3} cursor="pointer" _hover={{ bg: "gray.50" }} p={2} borderRadius="md" w="100%">
            <HiCog />
            <Text fontSize="sm">Settings</Text>
          </HStack>
        </VStack>
      </Box>
    </VStack>
  );

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
            <VStack p={3} spacing={4} h="100%">
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
              
              {/* 구독한 에이전트들 표시 (접힌 상태에서) */}
              <VStack spacing={2}>
                <Text fontSize="xs" color="gray.500" transform="rotate(-90deg)" whiteSpace="nowrap">
                  AGENTS
                </Text>
                {subscribedAgents.slice(0, 3).map((agent) => (
                  <Tooltip 
                    key={`${agent.agent_id}-${agent.agent_version}`}
                    label={`${agent.name} v${agent.agent_version}`} 
                    placement="right"
                  >
                    <Avatar
                      size="sm"
                      name={agent.name}
                      src={agent.icon_link || undefined}
                      bg={selectedAgent?.agent_id === agent.agent_id && selectedAgent?.agent_version === agent.agent_version ? "green.500" : "gray.400"}
                      cursor="pointer"
                      _hover={{ transform: "scale(1.1)" }}
                      transition="all 0.2s"
                      border={selectedAgent?.agent_id === agent.agent_id && selectedAgent?.agent_version === agent.agent_version ? "2px solid" : "none"}
                      borderColor="green.600"
                      onClick={() => handleSelectAgent(agent)}
                    />
                  </Tooltip>
                ))}
              </VStack>
              
              <Box flex={1} />
              
              <Tooltip label="Settings" placement="right">
                <IconButton
                  icon={<HiCog />}
                  size="md"
                  variant="ghost"
                  aria-label="Settings"
                />
              </Tooltip>
              
              {/* 사용자 아바타 (접힌 상태에서) */}
              {userInfo && (
                <Tooltip label={userInfo.username} placement="right">
                  <Avatar
                    size="sm"
                    name={userInfo.username}
                    src={userInfo.icon_link || undefined}
                    bg="blue.500"
                  />
                </Tooltip>
              )}
            </VStack>
          ) : (
            <SidebarContent 
              conversations={conversations}
              selectedConversationId={selectedConversationId}
              loading={loading}
              subscribedAgents={subscribedAgents}
              selectedAgent={selectedAgent}
              userInfo={userInfo}
              onNewChat={handleNewChat}
              onSelectConversation={handleSelectConversation}
              onEditConversation={handleEditConversation}
              onDeleteConversation={handleDeleteConversation}
              onSelectAgent={handleSelectAgent}
            />
          )}
        </Box>
      )}

      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="xs">
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader borderBottom="1px" borderColor="gray.200">
            Chats
          </DrawerHeader>
          <DrawerBody p={0}>
            <SidebarContent 
              conversations={conversations}
              selectedConversationId={selectedConversationId}
              loading={loading}
              subscribedAgents={subscribedAgents}
              selectedAgent={selectedAgent}
              userInfo={userInfo}
              onNewChat={handleNewChat}
              onSelectConversation={handleSelectConversation}
              onEditConversation={handleEditConversation}
              onDeleteConversation={handleDeleteConversation}
              onSelectAgent={handleSelectAgent}
            />
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Main Chat Area - ConversationWindow 컴포넌트 사용 */}
      <ConversationWindow
        availableModels={availableModels}
        selectedConversation={selectedConversation}
        selectedConversationId={selectedConversationId}
        messages={messages}
        message={message}
        messagesLoading={messagesLoading}
        sendingMessage={sendingMessage}
        selectedAgent={selectedAgent}
        selectedModel={selectedModel}
        onOpenSidebar={onOpen}
        onMessageChange={handleMessageChange}
        onSendMessage={handleSendMessage}
        onKeyPress={handleKeyPress}
        onSelectModel={onSelectModel}
      />
    </Flex>
  );
};

export default ChatView;