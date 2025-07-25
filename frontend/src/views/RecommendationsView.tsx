import React, { useState, useEffect } from 'react';
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
} from '@chakra-ui/react';
import { FiSend, FiSearch, FiPlus, FiMessageSquare, FiCalendar, FiClock, FiUser, FiMapPin } from 'react-icons/fi';
import { 
  getRecommendationsApiV1RecommendationsGet,
  getRecommendationByIdApiV1RecommendationsRecommendationIdGet,
  createRecommendationApiV1RecommendationsPost,
  chatCompletionWithAgentApiV1RecommendationsAgentIdCompletionPost,
  getRecommendationConversationApiV1RecommendationsAgentIdConversationGet,
} from '../client';
import type {
  RecommendationMaster,
  Recommendation,
  Agent,
  MessageResponse,
  PostRecommendationCompletionRequest,
} from '../client';


type Departments = 'Engineering' | 'Design' | 'Marketing' | 'Sales' | 'Support';
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
  const [showLanding, setShowLanding] = useState(true);
  
  
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  const sidebarBg = useColorModeValue('#F7FAFC', 'gray.900');
  const messageBg = useColorModeValue('gray.100', 'gray.700');
  const userMessageBg = useColorModeValue('blue.500', 'blue.600');
  const cardHoverShadow = useColorModeValue('lg', 'dark-lg');

  const DEPARTMENTS_STYLES = {
    Engineering: {
      id: "Engineering",
      color: 'blue',
      name: 'Engineering',
      bgGradient: 'linear(to-r, blue.400, blue.600)',
    },
    Design: {
      id: "Design",
      color: 'green',
      name: 'Design',
      bgGradient: 'linear(to-r, green.400, green.600)',
    },
    Marketing: {
      id: "Marketing",
      color: 'purple',
      name: 'Marketing',
      bgGradient: 'linear(to-r, purple.400, purple.600)',
    },
    Sales: {
      id: "Sales",
      color: 'orange',
      name: 'Sales',
      bgGradient: 'linear(to-r, orange.400, orange.600)',
    },
    Support: {
      id: "Support",
      color: 'teal',
      name: 'Support',
      bgGradient: 'linear(to-r, teal.400, teal.600)',
    },
  }

  // 추천 목록 불러오기
  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setIsLoading(true);
      const response = await getRecommendationsApiV1RecommendationsGet();
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
  };

  // 추천 상세 정보 불러오기
  const fetchRecommendationDetail = async (recommendationId: string) => {
    try {
      const response = await getRecommendationByIdApiV1RecommendationsRecommendationIdGet({
        path: { recommendation_id: recommendationId }
      });
      
      if (response.data) {
        setShowLanding(false);
        
        // 각 부서별 에이전트 표시
        const AgentCards: {[key in Departments]: Agent[]} = {
          Engineering: [],
          Design: [],
          Marketing: [],
          Sales: [],
          Support: [],
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
    }
  };

  // 히스토리 클릭 핸들러
  const handleHistoryClick = (rec: RecommendationMaster) => {
    setSelectedRecommendation(rec);
    fetchRecommendationDetail(rec.recommendation_id);

  };

  // 검색 처리
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setShowLanding(false);
    
    // 새로운 추천 생성
    try {
      const response = await createRecommendationApiV1RecommendationsPost({
        body: { work_details: searchQuery }
      });
      
      if (response.data?.recommendation) {
        fetchRecommendations();

        const AgentCards: {[key in Departments]: Agent[]} = {
          Engineering: [],
          Design: [],
          Marketing: [],
          Sales: [],
          Support: [],
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
        title: '추천 생성에 실패했습니다.',
        status: 'error',
        duration: 3000,
      });
    }
  };

  // 에이전트 선택 시 대화 불러오기
  const handleAgentSelect = async (agent: Agent) => {
    setSelectedAgent(agent);
    setIsDrawerOpen(true);
    
    try {
      const conversationResponse = await getRecommendationConversationApiV1RecommendationsAgentIdConversationGet({
        path: { agent_id: agent.agent_id }
      });
      
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
    setInputMessage('');

    try {
      const requestBody: PostRecommendationCompletionRequest = {
        action: 'next',
        conversation_id: conversationId || `conv_${Date.now()}`,
        parent_message_id: messages[messages.length - 1]?.message_id || null,
        llm: {
          issuer: 'openai',
          deployment_id: 'gpt-4'
        },
        agent: {
          agent_id: selectedAgent.agent_id,
          agent_version: selectedAgent.agent_version,
          department_id: selectedAgent.department_id || null
        }
      };

      // 사용자 메시지 추가
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
      setMessages(prev => [...prev, tempUserMessage]);

      // 스트리밍 응답 처리
      await chatCompletionWithAgentApiV1RecommendationsAgentIdCompletionPost({
        path: { agent_id: selectedAgent.agent_id },
        body: requestBody
      });

      // 응답 후 대화 다시 불러오기
      const updatedConversation = await getRecommendationConversationApiV1RecommendationsAgentIdConversationGet({
        path: { agent_id: selectedAgent.agent_id }
      });
      
      if (updatedConversation.data) {
        setMessages(updatedConversation.data.messages || []);
      }
    } catch (error) {
      toast({
        title: '메시지 전송에 실패했습니다.',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsSending(false);
    }
  };

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
      {/* 왼쪽 사이드바 */}
      <Box w="280px" bg={sidebarBg} borderRightWidth="1px" borderColor={borderColor}>
        <VStack h="full" spacing={0}>
          {/* 새 작업 시작 버튼 */}
          <Box p={4} w="full">
            <Button
              leftIcon={<FiPlus />}
              bgGradient="linear(to-r, purple.500, purple.600)"
              color="white"
              _hover={{ bgGradient: "linear(to-r, purple.600, purple.700)" }}
              w="full"
              size="md"
              borderRadius="lg"
              boxShadow="sm"
              onClick={() => {
                setShowLanding(true);
                setSearchResults({});
                setSelectedRecommendation(null);
                setRecommendationDetail(null);
              }}
            >
              새 작업 시작
            </Button>
          </Box>

          {/* 추천 히스토리 */}
          <Box flex={1} w="full" overflowY="auto" px={3} pb={4}>
            <VStack spacing={2} align="stretch">
              {isLoading ? (
                <Center py={10}>
                  <Spinner size="md" color="purple.500" />
                </Center>
              ) : (
                recommendations.map((rec) => (
                  <Card
                    key={rec.recommendation_id}
                    bg={selectedRecommendation?.recommendation_id === rec.recommendation_id ? 'purple.50' : 'white'}
                    borderWidth="1px"
                    borderColor={selectedRecommendation?.recommendation_id === rec.recommendation_id ? 'purple.200' : 'transparent'}
                    cursor="pointer"
                    onClick={() => handleHistoryClick(rec)}
                    _hover={{ 
                      shadow: 'sm',
                      borderColor: 'purple.200',
                      transform: 'translateY(-1px)'
                    }}
                    transition="all 0.2s"
                    borderRadius="lg"
                  >
                    <CardBody p={3}>
                      <VStack align="start" spacing={2}>
                        <Text fontWeight="semibold" fontSize="sm" noOfLines={1}>
                          {rec.title}
                        </Text>
                        <Text fontSize="xs" color="gray.600" noOfLines={2}>
                          {rec.description}
                        </Text>
                        <HStack spacing={2} flexWrap="wrap">
                          {rec.departments?.slice(0, 2).map((dept, idx) => (
                            <Badge 
                              key={idx} 
                              size="sm" 
                              colorScheme="purple" 
                              borderRadius="full"
                              fontSize="xs"
                            >
                              {dept}
                            </Badge>
                          ))}
                        </HStack>
                        <Text fontSize="xs" color="gray.500">
                          <Icon as={FiCalendar} boxSize={3} mr={1} />
                          {formatDate(rec.created_at || '')}
                        </Text>
                      </VStack>
                    </CardBody>
                  </Card>
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
                {Object.entries(searchResults).map(([deptId, agents]) => {
                  const dept = DEPARTMENTS_STYLES[deptId as Departments] || { id: deptId, name: deptId, color: 'purple', bgGradient: 'linear(to-r, purple.400, purple.600)' };
                  return (
                    <Box key={dept.id}>
                      <HStack mb={4}>
                        <Badge 
                          colorScheme={dept.color} 
                          fontSize="sm" 
                          px={3} 
                          py={1} 
                          borderRadius="full"
                        >
                          {dept.name}
                        </Badge>
                      </HStack>
                      
                      <Grid templateColumns="repeat(auto-fill, minmax(320px, 1fr))" gap={4}>
                        {agents.map((agent) => (
                          <Card
                            key={agent.agent_id}
                            bg="white"
                            borderWidth="1px"
                            borderColor="transparent"
                            _hover={{ 
                              shadow: cardHoverShadow,
                              transform: 'translateY(-4px)',
                              borderColor: 'purple.200'
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
                                  />
                                  <Box flex={1}>
                                    <Text fontWeight="bold" fontSize="md">{agent.name}</Text>
                                    <Text fontSize="sm" color="gray.500">{agent.department_name}</Text>
                                  </Box>
                                </HStack>
                                
                                <Text fontSize="sm" color="gray.600">
                                  {dept.name} 관련 업무를 전문적으로 도와드립니다
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
                                >
                                  상담 시작
                                </Button>
                              </VStack>
                            </CardBody>
                          </Card>
                        ))}
                      </Grid>
                    </Box>
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
        onClose={() => setIsDrawerOpen(false)}
        size="md"
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
                        <Text fontSize="sm">
                          {message.content.parts?.join(' ') || ''}
                        </Text>
                        <Text fontSize="xs" opacity={0.7} mt={1}>
                          {new Date(message.created_at).toLocaleTimeString('ko-KR', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </Text>
                      </Box>
                    </Flex>
                  ))}
                  {isSending && (
                    <Flex justify="flex-start">
                      <Box
                        bg="white"
                        px={4}
                        py={3}
                        borderRadius="2xl"
                        borderTopLeftRadius="sm"
                        boxShadow="sm"
                      >
                        <Spinner size="sm" color="purple.500" />
                      </Box>
                    </Flex>
                  )}
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