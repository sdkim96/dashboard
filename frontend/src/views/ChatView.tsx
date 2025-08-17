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
  Checkbox, // ✅ 툴 선택 UI용
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
  newConversationApiV1ConversationsNewPost,

  // 추가된 Tools API
  getToolsApiV1ToolsGet,
  getToolByIdApiV1ToolsToolIdGet,

  type ConversationMaster,
  type MessageRequest,
  type MessageResponse,
  type LlmModel,
  type User,
  type GenerateCompletionApiV1CompletionPostData,
  type PostGenerateCompletionRequest,
  type ToolRequest, // ✅ 쉼표 누락 주의
  type ToolMaster,
  type Tool,
  type GetToolsApiV1ToolsGetData,
} from '../client';

// 컴포넌트 import
import ConversationWindow from './ConversationWindow';

// 사이드바 컴포넌트 Props
interface SidebarContentProps {
  conversations: ConversationMaster[];
  selectedConversationId: string | null;
  loading: boolean;
  userInfo: User | null;
  onNewChat: () => void;
  onSelectConversation: (conversationId: string) => void;
  onEditConversation: (conversationId: string) => void;
  onDeleteConversation: (conversationId: string) => void;

  // ✅ 툴 섹션용
  tools: ToolMaster[];
  selectedToolIds: Set<string>;
  onToggleTool: (toolId: string) => void;
}

const ChatView: React.FC = () => {
  // States
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');
  const [conversations, setConversations] = useState<ConversationMaster[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [currentFinalParentMessageId, setCurrentFinalParentMessageId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [messagesLoading, setMessagesLoading] = useState<boolean>(false);
  const [sendingMessage, setSendingMessage] = useState<boolean>(false);
  
  // 사용자 정보 관련 state
  const [userInfo, setUserInfo] = useState<User | null>(null);
  const [availableModels, setAvailableModels] = useState<LlmModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<LlmModel | null>(null);

  // ✅ 툴 관련 state
  const [tools, setTools] = useState<ToolMaster[]>([]);
  const [selectedToolIds, setSelectedToolIds] = useState<Set<string>>(new Set());

  // Refs and hooks
  const { isOpen, onOpen, onClose } = useDisclosure();
  const isMobile = useBreakpointValue({ base: true, md: false });
  const toast = useToast();

  // Effects
  useEffect(() => {
    Promise.all([
      fetchUserInfo(),
      fetchConversations(),
      fetchTools(), // ✅ 툴 목록 로드
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

  const fetchNewConversation = async (): Promise<void> => {
    setLoading(true);
    try {
      const response = await newConversationApiV1ConversationsNewPost();
      if (response.data && response.data.conversation_id) {
        setSelectedConversationId(response.data.conversation_id);
        setCurrentFinalParentMessageId(response.data.parent_message_id || null);
      }
    } catch (error) {
      console.error('Failed to fetch new conversation:', error);
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
        path: { conversation_id: conversationId },
      });
      if (response.data && response.data.messages) {
        setMessages(response.data.messages);
        setCurrentFinalParentMessageId(
          response.data.messages.length > 0
            ? response.data.messages[response.data.messages.length - 1].message_id
            : null
        );
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
      console.log("currentFinalParentMessageId:", currentFinalParentMessageId);
    }
  };

  // ✅ Tools API
  const fetchTools = async (search?: string): Promise<void> => {
    try {
      const res = await getToolsApiV1ToolsGet({
        query: { page: 1, size: 50, search: search ?? undefined } as GetToolsApiV1ToolsGetData['query'],
      });
      if (res.data?.tools) setTools(res.data.tools);
    } catch (error) {
      console.error('Failed to fetch tools:', error);
      toast({
        title: 'Error',
        description: 'Failed to load tools',
        status: 'error',
        duration: 2500,
        isClosable: true,
      });
    }
  };

  // (옵션) 특정 툴 상세 조회 예시
  const fetchToolDetail = async (toolId: string): Promise<Tool | null> => {
    try {
      const res = await getToolByIdApiV1ToolsToolIdGet({
        path: { tool_id: toolId },
      });
      return res.data?.tool ?? null;
    } catch (error) {
      console.error('Failed to fetch tool detail:', error);
      return null;
    }
  };

  const toggleToolSelection = (toolId: string): void => {
    setSelectedToolIds(prev => {
      const next = new Set(prev);
      if (next.has(toolId)) next.delete(toolId);
      else next.add(toolId);
      return next;
    });
  };

  // 메시지 전송
  const handleSendMessage = async (): Promise<void> => {
    if (!message.trim() || !selectedConversationId) return;

    setSendingMessage(true);
    
    // 사용자 메시지 즉시 추가
    const newUserMessage: MessageResponse = {
      message_id: `msg-${Date.now()}`,
      parent_message_id: currentFinalParentMessageId || null,
      role: 'user',
      content: {
        type: 'text',
        parts: [message]
      },
      llm: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, newUserMessage]);
    setMessage('');

    // AI 응답 placeholder
    const aiMessageId = `msg-${Date.now() + 1}`;
    const aiResponseMessage: MessageResponse = {
      message_id: aiMessageId,
      role: 'assistant',
      content: {
        type: 'text',
        parts: ['']
      },
      llm: selectedModel || {
        issuer: 'openai',
        deployment_id: 'gpt-4',
        name: 'GPT-4',
        description: 'GPT-4 Model',
        icon_link: null
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, aiResponseMessage]);

    try {
      const selectedToolsBody: ToolRequest[] = Array.from(selectedToolIds).map(id => ({ tool_id: id }));

      const requestData: GenerateCompletionApiV1CompletionPostData = {
        body: {
          action: 'next',
          conversation_id: selectedConversationId,
          messages: [
            {
              content: {
                type: 'text',
                parts: [message]
              }
            }
          ] as MessageRequest[],
          llm: selectedModel as LlmModel,
          parent_message_id: messages.length > 0 ? messages[messages.length - 1].message_id : null,
          tools: selectedToolsBody, // ✅ 선택한 툴 반영
        } as PostGenerateCompletionRequest
      };

      // SSE 스트림 처리
      const response = await fetch('http://localhost:8000/api/v1/completion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // 'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(requestData.body),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let accumulatedStatus = '';
      let accumulatedMessage = '';
      let buffer = '';
      let currentEvent = '';
      let isDataStreaming = false;

      while (true) {
        try {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmedLine = line.trim();
            if (trimmedLine === '') continue;
            
            if (trimmedLine.startsWith('event:')) {
              currentEvent = trimmedLine.slice(6).trim();
              continue;
            }
            if (trimmedLine.startsWith('data:')) {
              const data = trimmedLine.slice(5).trim();
              try {
                const parsed = JSON.parse(data);
                if ('message' in parsed) {
                  switch(currentEvent) {
                    case 'start':
                      console.log('Stream started');
                      break;
                    case 'status':
                      if (!isDataStreaming) {
                        accumulatedStatus += parsed.message + '\n';
                        setMessages(prev => prev.map(msg => 
                          msg.message_id === aiMessageId 
                            ? { ...msg, content: { ...msg.content, parts: [accumulatedStatus] } }
                            : msg
                        ));
                      }
                      break;
                    case 'data':
                      if (!isDataStreaming) {
                        isDataStreaming = true;
                        accumulatedMessage = '';
                      }
                      if (parsed.message) {
                        accumulatedMessage += parsed.message;
                        setMessages(prev => prev.map(msg => 
                          msg.message_id === aiMessageId 
                            ? { ...msg, content: { ...msg.content, parts: [accumulatedMessage] } }
                            : msg
                        ));
                      }
                      break;
                    case 'done':
                      isDataStreaming = false;
                      if (parsed.message && parsed.message !== '....위 내용 전부 담길예정 ...') {
                        accumulatedMessage = parsed.message;
                        setMessages(prev => prev.map(msg => 
                          msg.message_id === aiMessageId 
                            ? { ...msg, content: { ...msg.content, parts: [accumulatedMessage] } }
                            : msg
                        ));
                      }
                      break;
                    default:
                      console.log(`Unknown event type: ${currentEvent}`, parsed);
                  }
                }
              } catch (e) {
                console.error('Failed to parse SSE data:', e, data);
              }
            }
          }
        } catch (readError) {
          console.error('Error reading stream:', readError);
          break;
        }
      }

      // 남은 버퍼 처리
      if (buffer.trim()) {
        const lines = buffer.split('\n');
        for (const line of lines) {
          const trimmedLine = line.trim();
          if (trimmedLine.startsWith('event:')) {
            currentEvent = trimmedLine.slice(6).trim();
          } else if (trimmedLine.startsWith('data:')) {
            const data = trimmedLine.slice(5).trim();
            try {
              const parsed = JSON.parse(data);
              if (parsed.message && currentEvent === 'data') {
                if (accumulatedMessage && !accumulatedMessage.endsWith('\n')) {
                  accumulatedMessage += '\n';
                }
                accumulatedMessage += parsed.message;
              }
            } catch (e) {
              console.error('Failed to parse remaining buffer:', e);
            }
          }
        }
        if (accumulatedMessage) {
          setMessages(prev => prev.map(msg => 
            msg.message_id === aiMessageId 
              ? { ...msg, content: { ...msg.content, parts: [accumulatedMessage] } }
              : msg
          ));
        }
      }

      if (!accumulatedMessage) {
        throw new Error('No response received from server');
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages(prev => prev.map(msg => 
        msg.message_id === aiMessageId 
          ? { ...msg, content: { ...msg.content, parts: ['죄송합니다. 응답을 생성하는 중 오류가 발생했습니다.'] } }
          : msg
      ));
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to send message',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setSendingMessage(false);
      fetchConversationDetails(selectedConversationId);
      fetchConversations();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewChat = (): void => {
    fetchNewConversation();
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
    userInfo,
    onNewChat, 
    onSelectConversation, 
    onEditConversation, 
    onDeleteConversation,

    // ✅ 툴 섹션
    tools,
    selectedToolIds,
    onToggleTool,
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

      {/* Conversations + Tools List */}
      <VStack flex={1} spacing={1} p={2} align="stretch" overflowY="auto">
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

        <Divider my={3} />

        {/* ✅ TOOLS 섹션 */}
        <Text fontSize="xs" fontWeight="semibold" color="gray.600" mb={2} px={1}>
          TOOLS
        </Text>

        {tools.length === 0 ? (
          <Box p={3} borderRadius="md" bg="gray.50">
            <Text fontSize="sm" color="gray.500">No tools available</Text>
          </Box>
        ) : (
          <VStack spacing={1} align="stretch">
            {tools.map(tool => {
              const checked = selectedToolIds.has(tool.tool_id);
              return (
                <HStack
                  key={tool.tool_id}
                    p={2}
                    borderRadius="md"
                    border="1px solid"
                    borderColor={checked ? 'green.400' : 'gray.200'}
                    bg={checked ? 'green.50' : 'white'}
                    _hover={{ bg: checked ? 'green.50' : 'gray.50' }}
                    cursor="pointer"
                    onClick={() => onToggleTool(tool.tool_id)}
                >
                  <Checkbox
                    isChecked={checked}
                    onChange={() => onToggleTool(tool.tool_id)}
                    mr={2}
                  />
                  <Avatar size="sm" src={tool.icon_link ?? undefined} name={tool.tool_name} />
                  <VStack align="start" spacing={0} flex={1}>
                    <Text fontSize="sm" noOfLines={1}>{tool.tool_name}</Text>
                    {tool.updated_at && (
                      <Text fontSize="xs" color="gray.500" noOfLines={1}>
                        Updated: {formatDate(tool.updated_at)}
                      </Text>
                    )}
                  </VStack>
                  {checked && (
                    <Badge colorScheme="green" variant="solid">✓</Badge>
                  )}
                </HStack>
              );
            })}
          </VStack>
        )}
      </VStack>

      <Divider />

      {/* Settings */}
      <Box p={4}>
        <VStack spacing={3}>
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
          w={isSidebarCollapsed ? "60px" : "320px"} // 🔧 살짝 넓힘(툴 섹션 가독성)
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

              <Box flex={1} />
              
              <Tooltip label="Settings" placement="right">
                <IconButton
                  icon={<HiCog />}
                  size="md"
                  variant="ghost"
                  aria-label="Settings"
                />
              </Tooltip>
              
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
              userInfo={userInfo}
              onNewChat={handleNewChat}
              onSelectConversation={handleSelectConversation}
              onEditConversation={handleEditConversation}
              onDeleteConversation={handleDeleteConversation}

              // ✅ 툴 섹션
              tools={tools}
              selectedToolIds={selectedToolIds}
              onToggleTool={toggleToolSelection}
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
              userInfo={userInfo}
              onNewChat={handleNewChat}
              onSelectConversation={handleSelectConversation}
              onEditConversation={handleEditConversation}
              onDeleteConversation={handleDeleteConversation}

              // ✅ 툴 섹션
              tools={tools}
              selectedToolIds={selectedToolIds}
              onToggleTool={toggleToolSelection}
            />
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Main Chat Area */}
      <ConversationWindow
        availableModels={availableModels}
        selectedConversation={selectedConversation}
        selectedConversationId={selectedConversationId}
        messages={messages}
        message={message}
        messagesLoading={messagesLoading}
        sendingMessage={sendingMessage}
        selectedModel={selectedModel}
        onOpenSidebar={onOpen}
        onMessageChange={(e) => setMessage(e.target.value)}
        onSendMessage={handleSendMessage}
        onKeyPress={handleKeyPress}
        onSelectModel={onSelectModel}
      />
    </Flex>
  );
};

export default ChatView;