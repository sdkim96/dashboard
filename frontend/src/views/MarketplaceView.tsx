import React, { useState, useEffect } from 'react';
import {
  Box,
  Text,
  SimpleGrid,
  Card,
  CardBody,
  Badge,
  Button,
  HStack,
  VStack,
  IconButton,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Input,
  InputGroup,
  InputLeftElement,
  Alert,
  AlertIcon,
  Divider,
  Wrap,
  WrapItem,
  useToast,
  Skeleton,
  SkeletonText,
  Icon,
  Center,
  Tooltip,
  Fade,
  ScaleFade,
  Portal,
  useColorModeValue,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverBody,
  PopoverArrow,
  PopoverCloseButton,
  Grid,
  GridItem
} from '@chakra-ui/react';
import { 
  HiSearch, 
  HiStar, 
  HiDownload, 
  HiUser, 
  HiCalendar, 
  HiTag,
  HiChevronRight,
  HiX
} from 'react-icons/hi';

// 정확한 API import
import { 
  getAvailableAgentsApiV1AgentsGet,
  getAgentApiV1AgentsAgentIdVersionAgentVersionGet,
  
} from '../client';

// 정확한 타입 import
import type {
  AgentMarketPlace,
  AgentDetail,
  Attribute,
} from '../client';

// 부서 타입 정의
import type { Departments } from '../types/departments';
import { DEPARTMENT_ICONS, DEPARTMENTS_STYLES } from '../types/departments';

// 확장된 AgentMarketPlace 타입 (department_name 포함)
interface AgentWithDepartment extends AgentMarketPlace {
  department_name: Departments;
}

// 부서 원형 컴포넌트
interface DepartmentCircleProps {
  department: Departments;
  agentCount: number;
  agents: AgentWithDepartment[];
  onAgentClick: (agent: AgentWithDepartment) => void;
  isSelected: boolean;
  onDepartmentClick: () => void;
}

const DepartmentCircle: React.FC<DepartmentCircleProps> = ({
  department,
  agentCount,
  agents,
  onAgentClick,
  isSelected,
  onDepartmentClick,
}) => {
  const departmentStyle = DEPARTMENTS_STYLES[department];
  const DepartmentIcon = DEPARTMENT_ICONS[department];
  const shadowColor = useColorModeValue(`${departmentStyle.color}.200`, `${departmentStyle.color}.800`);
  const bgColor = useColorModeValue('white', 'gray.800');

  return (
    <Box position="relative">
      {/* 부서 원 */}
      <Center>
        <Box
          position="relative"
          w={{ base: "120px", md: "140px", lg: "160px" }}
          h={{ base: "120px", md: "140px", lg: "160px" }}
          borderRadius="full"
          bgGradient={departmentStyle.bgGradient}
          cursor="pointer"
          transition="all 0.3s ease"
          transform={isSelected ? "scale(1.1)" : "scale(1)"}
          boxShadow={isSelected ? `0 20px 40px ${shadowColor}` : `0 4px 12px ${shadowColor}`}
          onClick={onDepartmentClick}
          zIndex={isSelected ? 10 : 1}
        >
          <Center h="full" flexDirection="column" color="white" p={4}>
            <Icon as={DepartmentIcon} boxSize={{ base: 8, md: 10 }} mb={2} />
            <Text fontSize={{ base: "xs", md: "sm" }} fontWeight="bold" textAlign="center">
              {departmentStyle.name}
            </Text>
            <Badge 
              mt={2} 
              colorScheme="whiteAlpha" 
              bg="whiteAlpha.300"
              color="white"
              fontSize="xs"
            >
              {agentCount} agents
            </Badge>
          </Center>
        </Box>
      </Center>

      {/* 에이전트 목록 - 선택되었을 때 표시 */}
      {isSelected && agents.length > 0 && (
        <Portal>
          <Box
            position="fixed"
            top="50%"
            left="50%"
            transform="translate(-50%, -50%)"
            zIndex={1000}
          >
            <ScaleFade in={isSelected} initialScale={0.9}>
              <Box
                bg={bgColor}
                p={6}
                borderRadius="xl"
                boxShadow="2xl"
                maxW="600px"
                maxH="70vh"
                overflowY="auto"
                border="1px solid"
                borderColor={`${departmentStyle.color}.200`}
              >
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between" mb={2}>
                    <HStack spacing={3}>
                      <Box
                        p={2}
                        borderRadius="lg"
                        bgGradient={departmentStyle.bgGradient}
                        color="white"
                      >
                        <Icon as={DepartmentIcon} boxSize={6} />
                      </Box>
                      <VStack align="start" spacing={0}>
                        <Text fontSize="lg" fontWeight="bold">
                          {departmentStyle.name}
                        </Text>
                        <Text fontSize="sm" color="gray.500">
                          {agentCount} available agents
                        </Text>
                      </VStack>
                    </HStack>
                    <IconButton
                      aria-label="Close"
                      icon={<HiX />}
                      size="sm"
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDepartmentClick();
                      }}
                    />
                  </HStack>

                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
                    {agents.map((agent) => (
                      <Card
                        key={`${agent.agent_id}-v${agent.agent_version}`}
                        size="sm"
                        cursor="pointer"
                        onClick={() => onAgentClick(agent)}
                        transition="all 0.2s"
                        borderWidth="1px"
                        borderColor={`${departmentStyle.color}.100`}
                        _hover={{
                          transform: "translateX(4px)",
                          boxShadow: "md",
                          borderColor: `${departmentStyle.color}.300`,
                          bg: `${departmentStyle.color}.50`
                        }}
                      >
                        <CardBody>
                          <HStack spacing={3}>
                            <VStack align="start" spacing={1} flex={1}>
                              <Text fontSize="sm" fontWeight="semibold" noOfLines={1}>
                                {agent.name}
                              </Text>
                              <HStack spacing={2} fontSize="xs" color="gray.500">
                                <HStack spacing={0.5}>
                                  <Icon as={HiStar} boxSize={3} color="orange.400" />
                                  <Text>4.8</Text>
                                </HStack>
                                <Text>•</Text>
                                <Text>v{agent.agent_version}</Text>
                              </HStack>
                              {agent.tags && agent.tags.length > 0 && (
                                <HStack spacing={1} mt={1}>
                                  {agent.tags.slice(0, 2).map((tag, index) => (
                                    <Badge 
                                      key={index}
                                      size="xs" 
                                      colorScheme={departmentStyle.color}
                                      variant="subtle"
                                      fontSize="10px"
                                    >
                                      {tag}
                                    </Badge>
                                  ))}
                                  {agent.tags.length > 2 && (
                                    <Text fontSize="10px" color="gray.500">
                                      +{agent.tags.length - 2}
                                    </Text>
                                  )}
                                </HStack>
                              )}
                            </VStack>
                            <Icon as={HiChevronRight} color="gray.400" boxSize={4} />
                          </HStack>
                        </CardBody>
                      </Card>
                    ))}
                  </SimpleGrid>
                </VStack>
              </Box>
            </ScaleFade>
          </Box>
        </Portal>
      )}
    </Box>
  );
};

// 에이전트 상세 모달 (동일하게 유지)
interface AgentDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  agent: AgentWithDepartment | null;
}

const AgentDetailModal: React.FC<AgentDetailModalProps> = ({ 
  isOpen, 
  onClose, 
  agent 
}) => {
  const [agentDetail, setAgentDetail] = useState<AgentDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (isOpen && agent) {
      fetchAgentDetail(agent.agent_id, agent.agent_version);
    }
  }, [isOpen, agent]);

  const fetchAgentDetail = async (agentId: string, agentVersion: number) => {
    setLoading(true);
    try {
      const response = await getAgentApiV1AgentsAgentIdVersionAgentVersionGet({
        path: { 
          agent_id: agentId, 
          agent_version: agentVersion 
        }
      });
      
      if (response.data && response.data.agent) {
        setAgentDetail(response.data.agent);
      }
    } catch (error) {
      console.error('Failed to fetch agent detail:', error);
      toast({
        title: 'Error',
        description: 'Failed to load agent details',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const departmentName = agentDetail?.department_name || agent?.department_name || 'Common';
  const departmentStyle = DEPARTMENTS_STYLES[departmentName as Departments] || DEPARTMENTS_STYLES.Common;
  const DepartmentIcon = DEPARTMENT_ICONS[departmentName] || DEPARTMENT_ICONS.Common;

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          {loading ? (
            <Skeleton height="32px" width="200px" />
          ) : (
            <HStack spacing={3}>
              <Box
                p={3}
                borderRadius="full"
                bgGradient={departmentStyle.bgGradient}
                color="white"
              >
                <Icon as={DepartmentIcon} boxSize={6} />
              </Box>
              <VStack align="start" spacing={0}>
                <Text fontSize="xl" fontWeight="bold">
                  {agentDetail?.name || agent?.name}
                </Text>
                <HStack spacing={2}>
                  <Badge colorScheme={departmentStyle.color}>
                    {departmentStyle.name}
                  </Badge>
                  <Text fontSize="sm" color="gray.600">
                    by {agentDetail?.author_name || 'Unknown'}
                  </Text>
                </HStack>
              </VStack>
            </HStack>
          )}
        </ModalHeader>
        
        <ModalCloseButton />
        
        <ModalBody>
          {loading ? (
            <VStack spacing={4} align="stretch">
              <SkeletonText mt="4" noOfLines={3} spacing="4" />
              <Skeleton height="20px" />
              <SkeletonText noOfLines={2} spacing="4" />
            </VStack>
          ) : agentDetail ? (
            <VStack spacing={6} align="stretch">
              <VStack align="stretch" spacing={3}>
                <Text fontSize="md" lineHeight="1.6">
                  {agentDetail.description}
                </Text>
                
                <HStack spacing={4} fontSize="sm" color="gray.600">
                  <HStack spacing={1}>
                    <HiUser />
                    <Text>Version {agentDetail.agent_version}</Text>
                  </HStack>
                  <HStack spacing={1}>
                    <HiCalendar />
                    <Text>{formatDate(agentDetail.created_at)}</Text>
                  </HStack>
                </HStack>
              </VStack>

              {agentDetail.tags && agentDetail.tags.length > 0 && (
                <VStack align="stretch" spacing={2}>
                  <HStack spacing={1}>
                    <HiTag />
                    <Text fontSize="sm" fontWeight="semibold">Tags</Text>
                  </HStack>
                  <Wrap spacing={2}>
                    {agentDetail.tags.map((tag, index) => (
                      <WrapItem key={index}>
                        <Badge colorScheme={departmentStyle.color} variant="subtle">
                          {tag}
                        </Badge>
                      </WrapItem>
                    ))}
                  </Wrap>
                </VStack>
              )}

              <Divider />

              {agentDetail.prompt && (
                <VStack align="stretch" spacing={2}>
                  <Text fontSize="sm" fontWeight="semibold">
                    Instructions
                  </Text>
                  <Box
                    p={4}
                    bg="gray.50"
                    borderRadius="md"
                    border="1px"
                    borderColor="gray.200"
                  >
                    <Text fontSize="sm" whiteSpace="pre-wrap">
                      {agentDetail.prompt}
                    </Text>
                  </Box>
                </VStack>
              )}

              <HStack justify="space-around" p={4} bg="gray.50" borderRadius="md">
                <VStack spacing={1}>
                  <HStack spacing={1} color="orange.500">
                    <HiStar />
                    <Text fontWeight="bold">4.8</Text>
                  </HStack>
                  <Text fontSize="xs" color="gray.600">Rating</Text>
                </VStack>
                <VStack spacing={1}>
                  <HStack spacing={1} color="blue.500">
                    <HiDownload />
                    <Text fontWeight="bold">1.2k</Text>
                  </HStack>
                  <Text fontSize="xs" color="gray.600">Downloads</Text>
                </VStack>
                <VStack spacing={1}>
                  <Text fontWeight="bold" color="green.500">
                    Free
                  </Text>
                  <Text fontSize="xs" color="gray.600">Price</Text>
                </VStack>
              </HStack>
            </VStack>
          ) : (
            <Alert status="error">
              <AlertIcon />
              Failed to load agent details
            </Alert>
          )}
        </ModalBody>

        <ModalFooter>
          <HStack spacing={3}>
            <Button variant="ghost" onClick={onClose}>
              Close
            </Button>
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

const MarketplaceView: React.FC = () => {
  const [allAgents, setAllAgents] = useState<AgentWithDepartment[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<AgentWithDepartment | null>(null);
  const [selectedDepartment, setSelectedDepartment] = useState<Departments | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    setLoading(true);
    try {
      const response = await getAvailableAgentsApiV1AgentsGet({
        query: {
          search: null,
          page: 1,
          size: 100
        }
      });
      
      if (response.data && response.data.agents) {
        const agentsWithDepartments = response.data.agents.map(agent => ({
          ...agent,
          department_name: (agent.department_name || 'Common') as Departments
        }));
        
        setAllAgents(agentsWithDepartments);
      }
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAgentClick = (agent: AgentWithDepartment) => {
    setSelectedAgent(agent);
    setSelectedDepartment(null); // 부서 모달을 닫음
    onOpen();
  };

  const handleDepartmentClick = (department: Departments) => {
    if (selectedDepartment === department) {
      setSelectedDepartment(null);
    } else {
      setSelectedDepartment(department);
    }
  };

  // 부서별로 에이전트 그룹화
  const agentsByDepartment = allAgents.reduce((acc, agent) => {
    const dept = agent.department_name;
    if (!acc[dept]) {
      acc[dept] = [];
    }
    acc[dept].push(agent);
    return acc;
  }, {} as Record<Departments, AgentWithDepartment[]>);

  // 검색 필터링
  const filteredAgentsByDepartment = Object.entries(agentsByDepartment).reduce((acc, [dept, agents]) => {
    const filtered = agents.filter(agent =>
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    );
    if (filtered.length > 0 || searchQuery === '') {
      acc[dept as Departments] = searchQuery === '' ? agents : filtered;
    }
    return acc;
  }, {} as Record<Departments, AgentWithDepartment[]>);

  // 사용 중인 부서만 추출
  const activeDepartments = Object.keys(filteredAgentsByDepartment) as Departments[];

  // 글로벌 스타일 추가 (애니메이션)
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes pulse {
        0% {
          opacity: 1;
          transform: scale(1);
        }
        50% {
          opacity: 0.6;
          transform: scale(1.05);
        }
        100% {
          opacity: 1;
          transform: scale(1);
        }
      }
    `;
    document.head.appendChild(style);
    return () => {
      document.head.removeChild(style);
    };
  }, []);

  return (
    <Box p={6} minH="100vh">
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <VStack spacing={4} align="stretch">
          <HStack justify="space-between" align="start">
            <VStack align="start" spacing={1}>
              <Text fontSize="3xl" fontWeight="bold">
                Agent Marketplace
              </Text>
              <Text color="gray.600" fontSize="md">
                Click a department to explore available AI agents
              </Text>
            </VStack>
            <Badge colorScheme="blue" variant="subtle" px={3} py={1} fontSize="sm">
              {allAgents.length} agents • {activeDepartments.length} departments
            </Badge>
          </HStack>
          
          {/* Search Bar */}
          <InputGroup maxW="400px">
            <InputLeftElement pointerEvents="none">
              <HiSearch color="gray.400" />
            </InputLeftElement>
            <Input
              placeholder="Search agents by name or tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              borderRadius="md"
            />
          </InputGroup>
        </VStack>

        {/* Department Circles Grid */}
        {loading ? (
          <SimpleGrid 
            columns={{ base: 2, sm: 3, md: 4, lg: 5 }} 
            spacing={{ base: 6, md: 8 }}
            justifyItems="center"
          >
            {Array.from({ length: 10 }).map((_, index) => (
              <Skeleton 
                key={index}
                w={{ base: "120px", md: "140px", lg: "160px" }}
                h={{ base: "120px", md: "140px", lg: "160px" }}
                borderRadius="full" 
              />
            ))}
          </SimpleGrid>
        ) : activeDepartments.length > 0 ? (
          <SimpleGrid 
            columns={{ base: 2, sm: 3, md: 4, lg: 5 }} 
            spacing={{ base: 6, md: 8 }}
            justifyItems="center"
          >
            {activeDepartments.map((department) => (
              <DepartmentCircle
                key={department}
                department={department}
                agentCount={filteredAgentsByDepartment[department]?.length || 0}
                agents={filteredAgentsByDepartment[department] || []}
                onAgentClick={handleAgentClick}
                isSelected={selectedDepartment === department}
                onDepartmentClick={() => handleDepartmentClick(department)}
              />
            ))}
          </SimpleGrid>
        ) : (
          <Center py={16}>
            <VStack spacing={4}>
              <Text fontSize="lg" color="gray.500">
                No agents found matching your search
              </Text>
              <Button 
                size="sm" 
                variant="ghost" 
                onClick={() => setSearchQuery('')}
                colorScheme="blue"
              >
                Clear search
              </Button>
            </VStack>
          </Center>
        )}
      </VStack>

      {/* Agent Detail Modal */}
      <AgentDetailModal
        isOpen={isOpen}
        onClose={onClose}
        agent={selectedAgent}
      />
    </Box>
  );
};

export default MarketplaceView;