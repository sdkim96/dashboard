import React, { useRef, useEffect } from 'react';
import {
  Box,
  Flex,
  IconButton,
  Text,
  Textarea,
  VStack,
  HStack,
  Avatar,
  Badge,
  useBreakpointValue,
  Skeleton,
  SkeletonText,
  Tooltip,
  Icon,
} from '@chakra-ui/react';
import { FaCheck, FaPaperPlane } from 'react-icons/fa';
import { HiMenu, HiChat } from 'react-icons/hi';

// API 및 타입 import
import {
  type ConversationMaster,
  type MessageResponse,
  type LlmModel,
  type Agent
} from '../client';

interface ConversationWindowProps {
  availableModels: LlmModel[];
  selectedConversation: ConversationMaster | undefined;
  selectedConversationId: string | null;
  messages: MessageResponse[];
  message: string;
  messagesLoading: boolean;
  sendingMessage: boolean;
  selectedAgent: Agent | null;
  selectedModel: LlmModel | null;
  onOpenSidebar: () => void;
  onMessageChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSendMessage: () => void;
  onKeyPress: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  onSelectModel: (model: LlmModel) => void;
}

const ConversationWindow: React.FC<ConversationWindowProps> = ({
  availableModels,
  selectedConversation,
  selectedConversationId,
  messages,
  message,
  messagesLoading,
  sendingMessage,
  selectedAgent,
  selectedModel,
  onOpenSidebar,
  onMessageChange,
  onSendMessage,
  onKeyPress,
  onSelectModel,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isMobile = useBreakpointValue({ base: true, md: false });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  

  return (
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
            onClick={onOpenSidebar}
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

      {/* Messages Area */}
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
            <div ref={messagesEndRef} />
          </VStack>
        )}
      </Box>

      {selectedConversationId && (
      <Box bg="white" borderTop="1px" borderColor="gray.200" p={4}>
        <Box maxW="3xl" mx="auto">
          {/* Model Selection - 더 컴팩트한 디자인 */}
          {availableModels.length > 0 && (
            <Box mb={2}>
              <HStack spacing={1} align="center" mb={1}>
                <Text fontSize="xs" fontWeight="medium" color="gray.600">
                  Model:
                </Text>
                <Text fontSize="xs" color="blue.600" fontWeight="semibold">
                  {selectedModel?.name || 'Select a model'}
                </Text>
              </HStack>
              
              <HStack spacing={1} overflowX="auto" pb={1}>
                {availableModels.map((model) => (
                  <Tooltip 
                    key={model.deployment_id} 
                    label={`${model.name} (${model.deployment_id})`}
                    placement="top"
                    hasArrow
                  >
                    <Box
                      onClick={() => onSelectModel(model)}
                      cursor="pointer"
                      position="relative"
                      transition="all 0.2s"
                      _hover={{ transform: "scale(1.1)" }}
                    >
                      <Avatar
                        size="xs"
                        name={model.name}
                        src={model.icon_link || undefined}
                        bg={selectedModel?.deployment_id === model.deployment_id ? "blue.500" : "gray.400"}
                        border={selectedModel?.deployment_id === model.deployment_id ? "2px solid" : "none"}
                        borderColor="blue.600"
                        boxSize="32px"
                      />
                      {selectedModel?.deployment_id === model.deployment_id && (
                        <Box
                          position="absolute"
                          bottom="-2px"
                          right="-2px"
                          bg="blue.600"
                          borderRadius="full"
                          p="1px"
                        >
                          <Icon as={FaCheck} color="white" boxSize="10px" />
                        </Box>
                      )}
                    </Box>
                  </Tooltip>
                ))}
              </HStack>
            </Box>
          )}

          <HStack spacing={3}>
            <Box flex={1} position="relative">
              {/* AutoResizeTextarea 커스텀 구현 */}
              <Textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => {
                  onMessageChange(e);
                  // 자동 높이 조절
                  const textarea = e.target;
                  textarea.style.height = 'auto';
                  textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
                }}
                onKeyPress={onKeyPress}
                placeholder="Type your message..."
                resize="none"
                minH="40px"
                maxH="200px"
                overflowY="auto"
                border="1px"
                borderColor="gray.300"
                borderRadius="lg"
                _focus={{
                  borderColor: "blue.500",
                  boxShadow: "0 0 0 1px blue.500"
                }}
                pr="50px"
                py={2}
                isDisabled={sendingMessage}
                transition="height 0.1s ease-in-out"
              />
              <IconButton
                icon={<Icon as={FaPaperPlane} />}
                size="sm"
                position="absolute"
                right="8px"
                bottom="8px"
                colorScheme="blue"
                borderRadius="md"
                isDisabled={!message.trim() || sendingMessage}
                isLoading={sendingMessage}
                onClick={onSendMessage}
                aria-label="Send Message"
                variant="solid"
              />
            </Box>
          </HStack>
          
          <Text fontSize="xs" color="gray.500" textAlign="center" mt={1}>
            Enter to send • Shift+Enter or Ctrl+Enter for new line
          </Text>
        </Box>
      </Box>
    )}
    </Flex>
  );
};

export default ConversationWindow;