import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Flex,
  IconButton,
  Text,
  Textarea,
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
  SkeletonText,
  Alert,
  AlertIcon,
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

// API 및 타입 import
import {
  getConversationsApiV1ConversationsGet,
  getConversationApiV1ConversationsConversationIdGet,
  getMeApiV1UserGet,
  type ConversationMaster,
  type MessageResponse,
  type GetConversationsResponse,
  type GetConversationResponse,
  type GetMeResponse,
  type Content,
  type LlmModel,
  type User,
  type Agent
} from '../client';



// 사이드바 컴포넌트 Props
interface SidebarContentProps {
  conversations: ConversationMaster[];
  selectedConversationId: string | null;
  loading: boolean;
  onNewChat: () => void;
  onSelectConversation: (conversationId: string) => void;
  onEditConversation: (conversationId: string) => void;
  onDeleteConversation: (conversationId: string) => void;
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
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isMobile = useBreakpointValue({ base: true, md: false });
  const toast = useToast();

  // Effects
  useEffect(() => {
    // 초기 데이터 로드
    Promise.all([
      fetchUserInfo(),
      fetchConversations()
    ]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (selectedConversationId) {
      fetchConversationDetails(selectedConversationId);
    }
  }, [selectedConversationId]);

  // Utility functions
  const scrollToBottom = (): void => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

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
          // 첫 번째 모델을 기본 선택
          if (response.data.llms.length > 0) {
            setSelectedModel(response.data.llms[0]);
          }
        }
        
        if (response.data.agents) {
          setSubscribedAgents(response.data.agents);
          // 첫 번째 에이전트를 기본 선택
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
        
        // 첫 번째 대화를 자동 선택
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
    
    // TODO: 실제 메시지 전송 API 호출
    // 현재는 시뮬레이션
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

    // Simulate AI response with selected model and agent
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
    // TODO: 새 채팅 생성 API 호출
    console.log('New chat');
  };

  const handleSelectConversation = (conversationId: string): void => {
    setSelectedConversationId(conversationId);
  };

  const handleEditConversation = (conversationId: string): void => {
    // TODO: 대화 편집 API 호출
    console.log('Edit conversation', conversationId);
  };

  const handleDeleteConversation = (conversationId: string): void => {
    // TODO: 대화 삭제 API 호출
    console.log('Delete conversation', conversationId);
  };

  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    setMessage(e.target.value);
  };

  const toggleSidebar = (): void => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
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
        {/* 구독한 에이전트들 표시 - 개선된 스타일 */}
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
                  onClick={() => setSelectedAgent(agent)}
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
          // 로딩 스켈레톤
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
                      onClick={() => setSelectedAgent(agent)}
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
              onNewChat={handleNewChat}
              onSelectConversation={handleSelectConversation}
              onEditConversation={handleEditConversation}
              onDeleteConversation={handleDeleteConversation}
            />
          )}
        </Box>
      )}

      {/* Mobile Drawer - 크기 줄임 */}
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
        {/* Header - 깔끔하게 정리 */}
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
            {selectedConversation?.title || 'Select a conversation'}
          </Text>
          
          {/* 현재 선택된 설정만 간단히 표시 */}
          <HStack spacing={2}>
            {selectedAgent && (
              <Badge size="sm" colorScheme="green" variant="outline">
                {selectedAgent.name}
              </Badge>
            )}
            {selectedModel && (
              <Badge size="sm" colorScheme="blue" variant="outline">
                {selectedModel.deployment_id}
              </Badge>
            )}
          </HStack>
        </Flex>

        {/* Messages Area - 개선된 메시지 스타일 */}
        <Box flex={1} overflowY="auto" bg="white">
          {messagesLoading ? (
            <VStack spacing={6} align="stretch" maxW="3xl" mx="auto" py={6}>
              {Array.from({ length: 3 }).map((_, index) => (
                <Box key={index} px={6} py={4}>
                  <HStack align="start" spacing={4}>
                    <Skeleton width="32px" height="32px" borderRadius="full" />
                    <VStack align="start" flex={1} spacing={2}>
                      <Skeleton height="16px" width="80px" />
                      <SkeletonText noOfLines={2} spacing="2" />
                    </VStack>
                  </HStack>
                </Box>
              ))}
            </VStack>
          ) : !selectedConversationId ? (
            <Flex align="center" justify="center" h="100%">
              <VStack spacing={3}>
                <HiChat size={48} color="gray.300" />
                <Text color="gray.500">Select a conversation to start chatting</Text>
              </VStack>
            </Flex>
          ) : messages.length === 0 ? (
            <Flex align="center" justify="center" h="100%">
              <VStack spacing={3}>
                <Text fontSize="lg" color="gray.600">Start a new conversation</Text>
                <Text fontSize="sm" color="gray.500">Send a message to begin</Text>
              </VStack>
            </Flex>
          ) : (
            <VStack spacing={0} align="stretch" maxW="3xl" mx="auto" py={6}>
              {messages.map((msg: MessageResponse) => (
                <Box key={msg.message_id} px={6} py={4}>
                  <Flex 
                    direction="row"
                    align="start" 
                    spacing={4}
                    gap={4}
                    justify="flex-start"
                  >
                    <Avatar
                      size="sm"
                      name={msg.role === 'user' ? 'User' : 'Assistant'}
                      src={msg.role === 'assistant' && msg.llm?.icon_link ? msg.llm.icon_link : undefined}
                      bg={msg.role === 'user' ? 'blue.500' : 'green.500'}
                      color="white"
                    />
                    
                    <VStack align="start" flex={1} spacing={2} maxW="80%">
                      <HStack spacing={2}>
                        <Text fontSize="sm" fontWeight="semibold" color="gray.600">
                          {msg.role === 'user' ? 'You' : 'Assistant'}
                        </Text>
                        {msg.llm && (
                          <Badge size="xs" colorScheme="green" variant="subtle">
                            {msg.llm.deployment_id}
                          </Badge>
                        )}
                      </HStack>
                      <Box
                        bg={msg.role === 'user' ? 'blue.500' : 'gray.100'}
                        color={msg.role === 'user' ? 'white' : 'gray.800'}
                        px={4}
                        py={3}
                        borderRadius="lg"
                        maxW="100%"
                        wordBreak="break-word"
                      >
                        <Text fontSize="md" lineHeight="1.6" whiteSpace="pre-wrap">
                          {msg.content.parts?.join('') || ''}
                        </Text>
                      </Box>
                    </VStack>
                  </Flex>
                </Box>
              ))}
              
              {/* 개선된 타이핑 인디케이터 */}
              {sendingMessage && (
                <Box px={6} py={4}>
                  <Flex direction="row" align="start" spacing={4} gap={4}>
                    <Avatar size="sm" bg="green.500" color="white" />
                    <VStack align="start" flex={1} spacing={2} maxW="80%">
                      <Text fontSize="sm" fontWeight="semibold" color="gray.600">
                        Assistant
                      </Text>
                      <Box bg="gray.100" px={4} py={3} borderRadius="lg">
                        <HStack spacing={1}>
                          <Box 
                            w={2} 
                            h={2} 
                            bg="gray.400" 
                            borderRadius="full" 
                            
                          />
                          <Box 
                            w={2} 
                            h={2} 
                            bg="gray.400" 
                            borderRadius="full" 
                            
                          />
                          <Box 
                            w={2} 
                            h={2} 
                            bg="gray.400" 
                            borderRadius="full" 
                            
                          />
                        </HStack>
                      </Box>
                    </VStack>
                  </Flex>
                </Box>
              )}
              <div ref={messagesEndRef} />
            </VStack>
          )}
        </Box>

        {/* Input Area */}
        {selectedConversationId && (
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
                    isDisabled={sendingMessage}
                  />
                  <IconButton
                    icon={<Text fontSize="lg">→</Text>}
                    size="sm"
                    position="absolute"
                    right="8px"
                    bottom="8px"
                    colorScheme="blue"
                    borderRadius="md"
                    isDisabled={!message.trim() || sendingMessage}
                    isLoading={sendingMessage}
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
        )}
      </Flex>
    </Flex>
  );
};

export default ChatView;