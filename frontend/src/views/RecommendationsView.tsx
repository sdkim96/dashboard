import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Box,
  Container,
  Grid,
  Card,
  CardBody,
  Text,
  Badge,
  Button,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  VStack,
  HStack,
  Input,
  InputGroup,
  InputRightElement,
  IconButton,
  Flex,
  Avatar,
  Heading,
  useColorModeValue,
  Spinner,
  useToast,
  Divider,
  Icon,
  Center,
  useDisclosure,
  Progress,
  Fade,
  ScaleFade,
  SlideFade,
} from '@chakra-ui/react';
import { keyframes } from '@emotion/react';
import { 
  FiSend, 
  FiSearch, 
  FiPlus, 
  FiMessageSquare, 
  FiCalendar, 
  FiClock, 
  FiUser, 
  FiMapPin,
  FiZap,
  FiCommand,
  FiLayers,
  FiRefreshCw,
  FiTarget,
  FiBriefcase,
  FiUsers,
  FiTrendingUp,
  FiAward,
  FiBookOpen,
  FiHeart,
  FiCompass,
  FiCpu,
  FiGlobe,
} from 'react-icons/fi';
import { 
  getRecommendationsApiV1RecommendationsGet,
  getRecommendationByIdApiV1RecommendationsRecommendationIdGet,
  createRecommendationApiV1RecommendationsPost,
  chatCompletionWithAgentApiV1RecommendationsRecommendationIdCompletionPost,
  newConversationApiV1ConversationsNewPost,
  getConversationByRecommendationApiV1RecommendationsRecommendationIdConversationsGet
  
} from '../client';
import type {
  RecommendationMaster,
  Recommendation,
  Agent,
  MessageResponse,
  PostRecommendationCompletionRequest,
} from '../client';

// 로딩 애니메이션 키프레임
const pulse = keyframes`
  0% { transform: scale(1); opacity: 0.7; }
  50% { transform: scale(1.05); opacity: 1; }
  100% { transform: scale(1); opacity: 0.7; }
`;

const float = keyframes`
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
`;

const slideIn = keyframes`
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
`;

// 로딩 중 표시할 팁들
const LOADING_TIPS = [
  { icon: FiTarget, text: "최적의 담당자를 찾고 있어요", color: "blue.400" },
  { icon: FiBriefcase, text: "업무 내용을 분석하고 있어요", color: "purple.400" },
  { icon: FiUsers, text: "각 부서별 전문가를 매칭하고 있어요", color: "green.400" },
  { icon: FiTrendingUp, text: "가장 효율적인 워크플로우를 설계하고 있어요", color: "orange.400" },
  { icon: FiAward, text: "최고의 결과를 위해 준비하고 있어요", color: "teal.400" },
];

import type { Departments } from '../types/departments';
import { DEPARTMENT_ICONS, DEPARTMENTS_STYLES } from '../types/departments';

const RecommendationChat = () => {
  const [recommendations, setRecommendations] = useState<RecommendationMaster[]>([]);
  const [selectedRecommendation, setSelectedRecommendation] = useState<RecommendationMaster | null>(null);
  const [recommendationDetail, setRecommendationDetail] = useState<Recommendation | null>(null);
  const [searchResults, setSearchResults] = useState<{[key: string]: Agent[]}>({});
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const [conversationId, setConversationId] = useState<string>('');
  const [currentFinalParentMessageId, setCurrentFinalParentMessageId] = useState<string | null>(null);

  const [showLanding, setShowLanding] = useState(true);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [currentTipIndex, setCurrentTipIndex] = useState(0);
  
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  const sidebarBg = useColorModeValue('gray.50', 'gray.900');
  const messageBg = useColorModeValue('gray.100', 'gray.700');
  const userMessageBg = useColorModeValue('blue.500', 'blue.600');
  const cardHoverShadow = useColorModeValue('xl', 'dark-lg');

  // 추천 목록 불러오기
  useEffect(() => {
    fetchRecommendations();
  }, []);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  

  // 로딩 중 팁 로테이션
  useEffect(() => {
    if (isLoadingDetail) {
      const tipInterval = setInterval(() => {
        setCurrentTipIndex((prev) => (prev + 1) % LOADING_TIPS.length);
      }, 2000);

      const progressInterval = setInterval(() => {
        setLoadingProgress((prev) => {
          if (prev >= 90) return prev;
          return prev + Math.random() * 15;
        });
      }, 300);

      return () => {
        clearInterval(tipInterval);
        clearInterval(progressInterval);
      };
    } else {
      setLoadingProgress(0);
      setCurrentTipIndex(0);
    }
  }, [isLoadingDetail]);

  const fetchRecommendations = async () => {
    let response;
    try {
      setIsLoading(true);
      response = await getRecommendationsApiV1RecommendationsGet();
      if (response.data?.recommendations) {
        setRecommendations(response.data.recommendations);
      }
    } catch (error) {
      toast({
        title: '추천 목록을 불러오는데 실패했습니다.',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsLoading(false);
    }
    return response?.data?.recommendations || [];
  };

  // 추천 상세 정보 불러오기
  const fetchRecommendationDetail = async (recommendationId: string) => {
    try {
      setIsLoadingDetail(true);
      setLoadingProgress(0);
      
      const response = await getRecommendationByIdApiV1RecommendationsRecommendationIdGet({
        path: { recommendation_id: recommendationId }
      });
      
      if (response.data) {
        setShowLanding(false);
        setLoadingProgress(100);
        
        // 로딩 완료 후 잠시 대기
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // 각 부서별 에이전트 표시
        const AgentCards: {[key in Departments]: Agent[]} = {
          Common: [],
          HR: [],
          Sales: [],
          Marketing: [],
          CustomerSupport: [],
          Finance: [],
          Planning: [],
          BusinessSupport: [],
          ProductDevelopment: [],
          InternationalSales: [],
        };
        for (const agentRec of response.data.recommendation?.agents || []) {
          const deptId = agentRec.department_name as Departments;
          if (AgentCards[deptId] && agentRec.agents) {
            AgentCards[deptId].push(...agentRec.agents.map(agent => ({
              ...agent,
              department_name: agentRec.department_name,
            })));
          }
        }
        setRecommendationDetail(response.data.recommendation);
        setSearchResults(AgentCards);
      }
    } catch (error) {
      toast({
        title: '추천 정보를 불러오는데 실패했습니다.',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsLoadingDetail(false);
    }
  };

  // 히스토리 클릭 핸들러
  const handleHistoryClick = (rec: RecommendationMaster) => {
    setSelectedRecommendation(rec);
    fetchRecommendationDetail(rec.recommendation_id);
  };

  const fetchNewConversation = async (): Promise<void> => {
      try {
        const response = await newConversationApiV1ConversationsNewPost();
        if (response.data && response.data.conversation_id) {
          setConversationId(response.data.conversation_id);
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
      }
    };

  // 검색 처리
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setShowLanding(false);
    setIsLoadingDetail(true);
    setLoadingProgress(0);
    
    // 새로운 추천 생성
    try {
      const response = await createRecommendationApiV1RecommendationsPost({
        body: { work_details: searchQuery }
      });
      
      if (response.data?.recommendation) {
        setLoadingProgress(100);
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const newRecs = await fetchRecommendations();
  
        const AgentCards: {[key in Departments]: Agent[]} = {
          Common: [],
          HR: [],
          Sales: [],
          Marketing: [],
          CustomerSupport: [],
          Finance: [],
          Planning: [],
          BusinessSupport: [],
          ProductDevelopment: [],
          InternationalSales: [],
        };

        for (const agentRec of response.data.recommendation?.agents || []) {
          const deptId = agentRec.department_name as Departments;
          if (AgentCards[deptId] && agentRec.agents) {
            AgentCards[deptId].push(...agentRec.agents.map(agent => ({
              ...agent,
              department_name: agentRec.department_name,
            })));
          }
        }

        for (const rec of newRecs) {
          if (rec.recommendation_id === response.data.recommendation?.recommendation_id) {
            setSelectedRecommendation(rec);
            break;
          }
        }
        
        setRecommendationDetail(response.data.recommendation);
        setSearchResults(AgentCards);
      }
    } catch (error) {
      toast({
        title: '추천 생성에 실패했습니다.',
        status: 'error',
        duration: 3000,
      });
      setSelectedRecommendation(selectedRecommendation);
    } finally {
      
      setIsLoadingDetail(false);
    }
  };

  // 에이전트 선택 시 대화 불러오기
  const handleAgentSelect = async (agent: Agent) => {
    setSelectedAgent(agent);
    setIsDrawerOpen(true);
    console.log("selected: ", selectedRecommendation);
    
      try {
        const conversationResponse = await getConversationByRecommendationApiV1RecommendationsRecommendationIdConversationsGet({
          path: { recommendation_id: selectedRecommendation?.recommendation_id || '' },
          query: { agent_id: agent.agent_id || '', agent_version: agent.agent_version || 0 }
        });

      if (conversationResponse.data && conversationResponse.data.status === 'error') {
        await fetchNewConversation();
        return;
      }

      if (conversationResponse.data) {
        setMessages(conversationResponse.data.messages || []);
        setConversationId(conversationResponse.data.conversation?.conversation_id || '');
      }
    } catch (error) {
      console.error('대화 불러오기 실패:', error);
    }
  };

  // 메시지 전송
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedAgent || isSending) return;

    setIsSending(true);
    const userMessage = inputMessage;
   
    const requestBody: PostRecommendationCompletionRequest = {
      action: 'next',
      conversation_id: conversationId || `conv_${Date.now()}`,
      parent_message_id: currentFinalParentMessageId || null,
      llm: {
        issuer: 'openai',
        deployment_id: 'gpt-4o-mini'
      },
      agent: {
        agent_id: selectedAgent.agent_id,
        agent_version: selectedAgent.agent_version,
        department_id: selectedAgent.department_name || null
      },
      messages: [
        {
          content: {
            type: 'text',
            parts: [userMessage]
          }
        }
      ]
    };

    const tempUserMessage: MessageResponse = {
      message_id: `temp_${Date.now()}`,
      role: 'user',
      content: {
        type: 'text',
        parts: [userMessage]
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      llm: null
    };

    const aiMessageId = `msg-${Date.now() + 1}`;
    const aiResponseMessage: MessageResponse = {
      message_id: aiMessageId,
      role: 'assistant',
      content: {
        type: 'text',
        parts: ['']
      },
      llm: {
        issuer: 'openai',
        deployment_id: 'gpt-4o-mini',
        name: 'GPT-4o-Mini',
        description: 'GPT-4o-Mini Model',
        icon_link: null
      },
      agent_id: selectedAgent?.agent_id || null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, tempUserMessage]);
    setMessages(prev => [...prev, aiResponseMessage]);
    setInputMessage('');

    const response = await fetch(`http://localhost:8000/api/v1/recommendations/${selectedRecommendation?.recommendation_id}/completion`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 인증 토큰이 있다면 추가
        // 'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(requestBody),
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
        
        // 마지막 줄이 완전하지 않을 수 있으므로 버퍼에 유지
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (trimmedLine === '') continue;
          
          // SSE 이벤트 파싱
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
                    // 시작 이벤트 - 보통 빈 메시지
                    console.log('Stream started');
                    break;

                  case 'error':
                    // 에러 이벤트
                    console.error('Stream error:', parsed.message);
                    toast({
                      title: '오류 발생',
                      description: parsed.message || '알 수 없는 오류가 발생했습니다.',
                      status: 'error',
                      duration: 3000,
                    })
                    throw new Error('No response received from server');
                    
                    
                  case 'status':
                    // 상태 메시지 표시 (🤔, 🧐 등)
                    
                    if (!isDataStreaming) {
                      console.log('Status:', parsed.message);
                      accumulatedStatus += parsed.message + '\n';

                      setMessages(prev => 
                        prev.map(msg => 
                          msg.message_id === aiMessageId 
                            ? {
                                ...msg,
                                content: {
                                  ...msg.content,
                                  parts: [accumulatedStatus]
                                }
                              }
                            : msg
                        )
                      );
                    }
                    break;
                    
                  case 'data':
                    // 실제 응답 메시지 - 스트리밍
                    if (!isDataStreaming) {
                      // 첫 번째 data 이벤트가 왔을 때 status 메시지를 지우고 시작
                      isDataStreaming = true;
                      accumulatedMessage = '';
                    }
                    
                    // 메시지를 누적
                    if (parsed.message) {
                      // 줄바꿈 추가 (마크다운 형식 유지)
                      accumulatedMessage += parsed.message;
                      
                      console.log('Streaming data chunk:', parsed.message);
                      
                      // 메시지 업데이트 (스트리밍 효과)
                      setMessages(prev => 
                        prev.map(msg => 
                          msg.message_id === aiMessageId 
                            ? {
                                ...msg,
                                content: {
                                  ...msg.content,
                                  parts: [accumulatedMessage]
                                }
                              }
                            : msg
                        )
                      );
                    }
                    break;
                    
                  case 'done':
                    // 완료 이벤트 - 전체 메시지가 담겨있음
                    console.log('Stream completed');
                    isDataStreaming = false;
                    
                    // done 이벤트의 메시지로 최종 확인 (옵션)
                    // 서버가 done에 전체 메시지를 보내는 경우 사용
                    if (parsed.message && parsed.message !== '....위 내용 전부 담길예정 ...') {
                      accumulatedMessage = parsed.message;
                      setMessages(prev => 
                        prev.map(msg => 
                          msg.message_id === aiMessageId 
                            ? {
                                ...msg,
                                content: {
                                  ...msg.content,
                                  parts: [accumulatedMessage]
                                }
                              }
                            : msg
                        )
                      );
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

    // 버퍼에 남은 데이터 처리
    if (buffer.trim()) {
      console.log('Remaining buffer:', buffer);
      // 남은 버퍼도 처리 시도
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
      
      // 최종 메시지 업데이트
      if (accumulatedMessage) {
        setMessages(prev => 
          prev.map(msg => 
            msg.message_id === aiMessageId 
              ? {
                  ...msg,
                  content: {
                    ...msg.content,
                    parts: [accumulatedMessage]
                  }
                }
              : msg
          )
        );
      }
    }

    // 스트림이 완료되었는데 메시지가 없는 경우
    if (!accumulatedMessage) {
      throw new Error('No response received from server');
    }
    try {
      const conversationResponse = await getConversationByRecommendationApiV1RecommendationsRecommendationIdConversationsGet({
        path: { recommendation_id: selectedRecommendation?.recommendation_id || '' },
        query: { agent_id: selectedAgent.agent_id || '', agent_version: selectedAgent.agent_version || 0 }
      });

      if (conversationResponse.data && conversationResponse.data.status === 'error') {
        await fetchNewConversation();
        return;
      }

      if (conversationResponse.data) {
        // 전체 메시지를 overwrite (기존 메시지 대체)
        setMessages(conversationResponse.data.messages || []);
        setConversationId(conversationResponse.data.conversation?.conversation_id || '');
      }
    } catch (error) {
      console.error('대화 불러오기 실패:', error);
      toast({
        title: '대화 불러오기 실패',
        description: '대화 내용을 불러오는 데 실패했습니다.',
        status: 'error',
        duration: 3000,
      });
    }
    setIsSending(false);
  };
  

  const handleDrawerClose = () => {
    setIsDrawerOpen(false);
    setSelectedAgent(null);
    setMessages([]);
    setInputMessage('');
    setConversationId('');
    setCurrentFinalParentMessageId(null);
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', { 
      month: '2-digit', 
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }).replace(/\. /g, '. ');
  };

  return (
    <Flex h="100vh" overflow="hidden">
      {/* 왼쪽 사이드바 - 라이트 테마 with 모던 하이라이트 */}
      <Box 
        w="280px" 
        bg={sidebarBg} 
        borderRightWidth="1px" 
        borderColor={borderColor}
        position="relative"
        overflow="hidden"
      >
        {/* 배경 그라데이션 효과 - 더 은은하게 */}
        <Box
          position="absolute"
          top="-50%"
          right="-50%"
          w="200%"
          h="200%"
          bgGradient="radial(purple.100 0%, transparent 70%)"
          opacity="0.3"
          pointerEvents="none"
        />
        
        <VStack h="full" spacing={0} position="relative">
          {/* 새 작업 시작 버튼 - 그라데이션 하이라이트 */}
          <Box p={4} w="full">
            <Button
              bg="white"
              color="gray.700"
              border="1px solid"
              borderColor="gray.200"
              boxShadow="sm"
              _hover={{
                bg: "white",
                borderColor: "transparent",
                boxShadow: "0 4px 20px rgba(138, 97, 255, 0.15)",
                transform: "translateY(-2px)",
                // 텍스트(span)와 아이콘(svg) 모두 타겟팅
                "& span, & svg": {
                  bgGradient: "linear(to-r, purple.400, pink.400, blue.400)",
                  bgClip: "text",
                  color: "transparent"
                }
              }}
              _active={{
                transform: "translateY(0)",
                boxShadow: "0 2px 10px rgba(138, 97, 255, 0.1)"
              }}
              w="full"
              h="48px"
              fontSize="md"
              fontWeight="medium"
              borderRadius="xl"
              transition="all 0.2s"
              position="relative"
              overflow="hidden"
              onClick={() => {
                setShowLanding(true);
                setSearchResults({});
                setSelectedRecommendation(null);
                setRecommendationDetail(null);
              }}
              _before={{
                content: '""',
                position: "absolute",
                top: "-2px",
                left: "-2px",
                right: "-2px",
                bottom: "-2px",
                bgGradient: "linear(to-r, purple.400, pink.400, blue.400)",
                borderRadius: "xl",
                opacity: 0,
                transition: "opacity 0.3s",
                zIndex: -1
              }}
            >
              <span>새 작업 시작</span>
            </Button>
          </Box>

          <Divider borderColor={borderColor} />

          {/* 추천 히스토리 헤더 */}
          <Box px={4} py={3}>
            <Text color="gray.500" fontSize="xs" fontWeight="semibold" letterSpacing="wider">
              최근 작업
            </Text>
          </Box>

          {/* 추천 히스토리 리스트 */}
          <Box flex={1} w="full" overflowY="auto" px={3} pb={4}>
            <VStack spacing={2} align="stretch">
              {isLoading ? (
                <Center py={10}>
                  <Spinner size="md" color="purple.400" />
                </Center>
              ) : (
                recommendations.map((rec, index) => (
                  <ScaleFade in={true} delay={index * 0.05} key={rec.recommendation_id}>
                    <Card
                      bg={selectedRecommendation?.recommendation_id === rec.recommendation_id 
                        ? 'white' 
                        : 'white'}
                      borderWidth="1px"
                      borderColor={selectedRecommendation?.recommendation_id === rec.recommendation_id 
                        ? 'transparent' 
                        : 'gray.200'}
                      cursor="pointer"
                      onClick={() => handleHistoryClick(rec)}
                      _hover={{ 
                        borderColor: 'transparent',
                        transform: 'translateX(4px)',
                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)'
                      }}
                      transition="all 0.2s"
                      borderRadius="lg"
                      overflow="hidden"
                      position="relative"
                      boxShadow={selectedRecommendation?.recommendation_id === rec.recommendation_id 
                        ? '0 4px 20px rgba(138, 97, 255, 0.15)' 
                        : 'sm'}
                    >
                      {/* 선택된 아이템 그라데이션 보더 효과 */}
                      {selectedRecommendation?.recommendation_id === rec.recommendation_id && (
                        <>
                          <Box
                            position="absolute"
                            top="-1px"
                            left="-1px"
                            right="-1px"
                            bottom="-1px"
                            bgGradient="linear(135deg, purple.400, pink.400, blue.400)"
                            borderRadius="lg"
                            zIndex={0}
                          />
                          <Box
                            position="absolute"
                            top="1px"
                            left="1px"
                            right="1px"
                            bottom="1px"
                            bg="white"
                            borderRadius="lg"
                            zIndex={1}
                          />
                        </>
                      )}
                      
                      <CardBody p={3} position="relative" zIndex={2}>
                        <VStack align="start" spacing={2}>
                          <Text 
                            fontWeight="semibold" 
                            fontSize="sm" 
                            color="gray.800" 
                            noOfLines={1}
                          >
                            {rec.title}
                          </Text>
                          <Text fontSize="xs" color="gray.600" noOfLines={2}>
                            {rec.description}
                          </Text>
                          <HStack spacing={2} flexWrap="wrap">
                            {rec.departments?.slice(0, 2).map((dept, idx) => {
                              const deptKey = dept as Departments;
                              const deptStyle = DEPARTMENTS_STYLES[deptKey];
                              return (
                                <Badge 
                                  key={idx} 
                                  size="sm" 
                                  bg={selectedRecommendation?.recommendation_id === rec.recommendation_id 
                                    ? `${deptStyle?.color || 'purple'}.50`
                                    : 'gray.100'}
                                  color={selectedRecommendation?.recommendation_id === rec.recommendation_id 
                                    ? `${deptStyle?.color || 'purple'}.600`
                                    : 'gray.600'}
                                  borderRadius="full"
                                  fontSize="xs"
                                  px={2}
                                  py={0.5}
                                  border="1px solid"
                                  borderColor={selectedRecommendation?.recommendation_id === rec.recommendation_id 
                                    ? `${deptStyle?.color || 'purple'}.200`
                                    : 'transparent'}
                                >
                                  <HStack spacing={1}>
                                    <Icon as={DEPARTMENT_ICONS[deptKey] || FiLayers} boxSize={3} />
                                    <Text>{dept}</Text>
                                  </HStack>
                                </Badge>
                              );
                            })}
                          </HStack>
                          <HStack spacing={2} color="gray.500" fontSize="xs">
                            <Icon as={FiCalendar} boxSize={3} />
                            <Text>{formatDate(rec.created_at || '')}</Text>
                          </HStack>
                        </VStack>
                      </CardBody>
                    </Card>
                  </ScaleFade>
                ))
              )}
            </VStack>
          </Box>
        </VStack>
      </Box>

      {/* 메인 콘텐츠 영역 */}
      <Box flex={1} overflow="hidden" bg={useColorModeValue('gray.50', 'gray.900')}>
        {showLanding ? (
          /* 랜딩 페이지 - 검색창만 */
          <Center h="full" p={8}>
            <VStack spacing={6} maxW="700px" w="full">
              <VStack spacing={3}>
                <Heading size="2xl" fontWeight="bold">무엇을 도와드릴까요?</Heading>
                <Text fontSize="lg" color="gray.600" textAlign="center">
                  업무에 필요한 내용을 자세히 설명해주세요
                </Text>
              </VStack>
              
              <Box w="full" position="relative">
                <Input
                  placeholder="예: 2월 15일 그랜드 호텔에서 열리는 신제품 런칭 행사 기획이 필요합니다..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  h="56px"
                  fontSize="md"
                  borderRadius="full"
                  pr="60px"
                  bg="white"
                  borderWidth="1px"
                  borderColor="gray.200"
                  _focus={{
                    borderColor: 'blue.500',
                    boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)'
                  }}
                />
                <IconButton
                  aria-label="Search"
                  icon={<FiSearch size={20} />}
                  onClick={handleSearch}
                  colorScheme="blue"
                  borderRadius="full"
                  size="md"
                  position="absolute"
                  right="8px"
                  top="50%"
                  transform="translateY(-50%)"
                />
              </Box>
            </VStack>
          </Center>
        ) : isLoadingDetail ? (
          /* 로딩 화면 - 인터랙티브한 애니메이션 */
          <Center h="full" p={8}>
            <VStack spacing={8} maxW="500px" w="full">
              {/* 메인 로딩 애니메이션 */}
              <Box position="relative" w="120px" h="120px">
                <Box
                  position="absolute"
                  inset="0"
                  borderRadius="full"
                  bgGradient="linear(to-r, purple.400, pink.400)"
                  animation={`${pulse} 2s ease-in-out infinite`}
                  opacity="0.3"
                />
                <Center
                  position="absolute"
                  inset="0"
                  borderRadius="full"
                  bg="white"
                  boxShadow="xl"
                  animation={`${float} 3s ease-in-out infinite`}
                >
                  <Icon 
                    as={LOADING_TIPS[currentTipIndex].icon} 
                    boxSize={12} 
                    color={LOADING_TIPS[currentTipIndex].color}
                  />
                </Center>
              </Box>

              {/* 로딩 텍스트 */}
              <VStack spacing={4} w="full">
                <Fade in={true} key={currentTipIndex}>
                  <Text 
                    fontSize="lg" 
                    fontWeight="medium" 
                    textAlign="center"
                    color="gray.700"
                  >
                    {LOADING_TIPS[currentTipIndex].text}
                  </Text>
                </Fade>

                {/* 프로그레스 바 */}
                <Box w="full" maxW="300px">
                  <Progress 
                    value={loadingProgress} 
                    size="sm" 
                    colorScheme="purple"
                    borderRadius="full"
                    hasStripe
                    isAnimated
                  />
                  <HStack justify="space-between" mt={2}>
                    <Text fontSize="xs" color="gray.500">분석 중...</Text>
                    <Text fontSize="xs" color="gray.500">{Math.round(loadingProgress)}%</Text>
                  </HStack>
                </Box>
              </VStack>

              {/* 로딩 중 팁 아이콘들 */}
              <HStack spacing={4} mt={8}>
                {LOADING_TIPS.map((tip, index) => (
                  <Box
                    key={index}
                    p={2}
                    borderRadius="lg"
                    bg={index === currentTipIndex ? 'purple.50' : 'transparent'}
                    transition="all 0.3s"
                  >
                    <Icon
                      as={tip.icon}
                      boxSize={6}
                      color={index === currentTipIndex ? tip.color : 'gray.400'}
                      opacity={index === currentTipIndex ? 1 : 0.4}
                    />
                  </Box>
                ))}
              </HStack>
            </VStack>
          </Center>
        ) : (
          /* 검색 결과 - 추천 상세 및 부서별 에이전트 카드 */
          <Box h="full" overflowY="auto">
            {/* 추천 상세 정보 헤더 */}
            {recommendationDetail && (
              <Box bg="white" px={8} py={6} borderBottomWidth="1px" borderColor={borderColor}>
                <VStack align="start" spacing={4}>
                  <Heading size="lg">{selectedRecommendation?.title || '새로운 추천'}</Heading>
                  <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
                    <HStack>
                      <Icon as={FiCalendar} color="gray.500" />
                      <Box>
                        <Text fontSize="xs" color="gray.500">언제</Text>
                        <Text fontSize="sm" fontWeight="medium">{recommendationDetail.work_when}</Text>
                      </Box>
                    </HStack>
                    <HStack>
                      <Icon as={FiMapPin} color="gray.500" />
                      <Box>
                        <Text fontSize="xs" color="gray.500">어디서</Text>
                        <Text fontSize="sm" fontWeight="medium">{recommendationDetail.work_where}</Text>
                      </Box>
                    </HStack>
                    <HStack>
                      <Icon as={FiUser} color="gray.500" />
                      <Box>
                        <Text fontSize="xs" color="gray.500">누구와</Text>
                        <Text fontSize="sm" fontWeight="medium">{recommendationDetail.work_whom}</Text>
                      </Box>
                    </HStack>
                  </Grid>
                  <Text color="gray.600">{recommendationDetail.work_details}</Text>
                </VStack>
              </Box>
            )}

            {/* 부서별 에이전트 카드 */}
            <Box p={8}>
              <VStack spacing={8} align="stretch">
                {Object.entries(searchResults).map(([deptId, agents], deptIndex) => {
                  const dept = DEPARTMENTS_STYLES[deptId as Departments] || { id: deptId, name: deptId, color: 'purple', bgGradient: 'linear(to-r, purple.400, purple.600)' };
                  const DeptIcon = DEPARTMENT_ICONS[deptId as Departments] || FiLayers;
                  
                  return (
                    <SlideFade in={true} offsetY="20px" delay={deptIndex * 0.1} key={dept.id}>
                      <Box>
                        <HStack mb={4}>
                          <Badge 
                            colorScheme={dept.color} 
                            fontSize="sm" 
                            px={3} 
                            py={1} 
                            borderRadius="full"
                            display="flex"
                            alignItems="center"
                          >
                            <Icon as={DeptIcon} mr={2} />
                            {dept.name}
                          </Badge>
                        </HStack>
                        
                        <Grid templateColumns="repeat(auto-fill, minmax(320px, 1fr))" gap={4}>
                          {agents.map((agent, agentIndex) => (
                            <ScaleFade in={true} delay={(deptIndex * 0.1) + (agentIndex * 0.05)} key={agent.agent_id}>
                              <Card
                                bg="white"
                                borderWidth="1px"
                                borderColor="transparent"
                                _hover={{ 
                                  shadow: cardHoverShadow,
                                  transform: 'translateY(-4px)',
                                  borderColor: `${dept.color}.200`
                                }}
                                transition="all 0.3s"
                                cursor="pointer"
                                onClick={() => handleAgentSelect(agent)}
                                borderRadius="xl"
                                overflow="hidden"
                              >
                                <Box h="4px" bgGradient={dept.bgGradient} />
                                <CardBody p={5}>
                                  <VStack align="start" spacing={4}>
                                    <HStack spacing={3}>
                                      <Avatar 
                                        size="md" 
                                        name={agent.name}
                                        bg={`${dept.color}.500`}
                                        icon={<Icon as={DeptIcon} boxSize={6} />}
                                      />
                                      <Box flex={1}>
                                        <Text fontWeight="bold" fontSize="md">{agent.name}</Text>
                                        <Text fontSize="sm" color="gray.500">{agent.department_name}</Text>
                                      </Box>
                                    </HStack>
                                    
                                    <Text fontSize="sm" color="gray.600">
                                      {agent.description || `${dept.name} 에이전트입니다. 업무에 대한 질문을 해보세요!`}
                                    </Text>
                                    
                                    <HStack spacing={2} flexWrap="wrap">
                                      {agent.tags?.map((tag, idx) => (
                                        <Badge key={idx} size="sm" variant="subtle" colorScheme={dept.color}>
                                          {tag}
                                        </Badge>
                                      ))}
                                    </HStack>
                                    
                                    <Button
                                      size="sm"
                                      colorScheme={dept.color}
                                      variant="ghost"
                                      w="full"
                                      rightIcon={<FiMessageSquare />}
                                      _hover={{
                                        bg: `${dept.color}.50`,
                                        transform: 'translateX(4px)'
                                      }}
                                      transition="all 0.2s"
                                    >
                                      상담 시작
                                    </Button>
                                  </VStack>
                                </CardBody>
                              </Card>
                            </ScaleFade>
                          ))}
                        </Grid>
                      </Box>
                    </SlideFade>
                  );
                })}
              </VStack>
            </Box>
          </Box>
        )}
      </Box>

      {/* 채팅 Drawer */}
      <Drawer
        isOpen={isDrawerOpen}
        placement="right"
        onClose={handleDrawerClose}
        size="lg"
      >
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px">
            <HStack spacing={3}>
              <Avatar size="sm" name={selectedAgent?.name} bg="purple.500" />
              <Box>
                <Text fontSize="lg" fontWeight="semibold">{selectedAgent?.name}</Text>
                <Text fontSize="sm" color="gray.500">{selectedAgent?.department_name}</Text>
              </Box>
            </HStack>
          </DrawerHeader>

          <DrawerBody p={0}>
            <Flex direction="column" h="full">
              {/* 메시지 영역 */}
              <Box flex={1} overflowY="auto" p={4} bg={useColorModeValue('gray.50', 'gray.800')}>
                <VStack spacing={4} align="stretch">
                  {messages.map((message) => (
                    <Flex
                      key={message.message_id}
                      justify={message.role === 'user' ? 'flex-end' : 'flex-start'}
                    >
                      <Box
                        maxW="80%"
                        bg={message.role === 'user' ? userMessageBg : 'white'}
                        color={message.role === 'user' ? 'white' : 'gray.800'}
                        px={4}
                        py={3}
                        borderRadius="2xl"
                        borderTopRightRadius={message.role === 'user' ? 'sm' : '2xl'}
                        borderTopLeftRadius={message.role === 'user' ? '2xl' : 'sm'}
                        boxShadow="sm"
                      >
                        <Box
                          sx={{
                            '& p': { mb: 2, lineHeight: 1.6 },
                            '& p:last-child': { mb: 0 },
                            '& h1': { fontSize: '2xl', fontWeight: 'bold', mt: 4, mb: 2 },
                            '& h2': { fontSize: 'xl', fontWeight: 'bold', mt: 3, mb: 2 },
                            '& h3': { fontSize: 'lg', fontWeight: 'bold', mt: 2, mb: 1 },
                            '& ul': { pl: 6, mb: 2 },
                            '& ol': { pl: 6, mb: 2 },
                            '& li': { mb: 1 },
                            '& blockquote': { 
                              pl: 4, 
                              borderLeft: '4px solid',
                              borderColor: 'gray.300',
                              fontStyle: 'italic',
                              my: 2 
                            },
                            '& code': {
                              bg: message.role === 'user' ? 'whiteAlpha.300' : 'gray.200',
                              px: 1,
                              py: 0.5,
                              borderRadius: 'sm',
                              fontSize: 'sm',
                              fontFamily: 'monospace'
                            },
                            '& pre': {
                              bg: message.role === 'user' ? 'whiteAlpha.300' : 'gray.800',
                              color: message.role === 'user' ? 'white' : 'gray.100',
                              p: 3,
                              borderRadius: 'md',
                              overflowX: 'auto',
                              my: 2,
                              '& code': {
                                bg: 'transparent',
                                p: 0,
                                color: 'inherit'
                              }
                            },
                            '& table': {
                              borderCollapse: 'collapse',
                              my: 2,
                              width: '100%'
                            },
                            '& th, & td': {
                              border: '1px solid',
                              borderColor: 'gray.300',
                              p: 2
                            },
                            '& th': {
                              bg: 'gray.100',
                              fontWeight: 'bold'
                            },
                            '& a': {
                              color: 'blue.500',
                              textDecoration: 'underline',
                              _hover: { color: 'blue.600' }
                            },
                            '& hr': {
                              my: 4,
                              borderColor: 'gray.300'
                            }
                          }}
                        >
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              // 코드 블록에 복사 버튼 추가 (선택사항)
                              pre: ({ children }) => (
                                <Box position="relative">
                                  <Box as="pre" overflow="auto">
                                    {children}
                                  </Box>
                                </Box>
                              ),
                            }}
                          >
                            {message.content.parts?.join('') || ''}
                          </ReactMarkdown>
                        </Box>
                        <Text fontSize="xs" opacity={0.7} mt={1}>
                          {new Date(message.created_at).toLocaleTimeString('ko-KR', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </Text>
                      </Box>
                    </Flex>
                  ))}
                  <div ref={messagesEndRef} />
                </VStack>
              </Box>

              {/* 입력 영역 */}
              <Box p={4} bg="white" borderTopWidth="1px" borderColor={borderColor}>
                <HStack>
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="메시지를 입력하세요..."
                    disabled={isSending}
                    borderRadius="full"
                    bg={useColorModeValue('gray.50', 'gray.700')}
                    borderColor="transparent"
                    _focus={{
                      borderColor: 'purple.500',
                      boxShadow: '0 0 0 1px var(--chakra-colors-purple-500)'
                    }}
                  />
                  <IconButton
                    aria-label="Send message"
                    icon={<FiSend />}
                    onClick={handleSendMessage}
                    colorScheme="purple"
                    borderRadius="full"
                    isLoading={isSending}
                    isDisabled={!inputMessage.trim()}
                  />
                </HStack>
              </Box>
            </Flex>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </Flex>
  );
};

export default RecommendationChat;