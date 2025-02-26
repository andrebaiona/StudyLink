#!/bin/bash

# Define colors
RESET="\033[0m"
BOLD="\033[1m"
RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
BLUE="\033[94m"

echo -e "${BOLD}${YELLOW}⚠ WARNING: This action will stop and rebuild your Docker containers.${RESET}"
echo -e "${RED}${BOLD}❗ All database data will be permanently deleted!${RESET}"
echo -e "${BOLD}Do you want to continue? (y/n)${RESET}"
read -r CONFIRMATION

if [[ "$CONFIRMATION" == "y" ]]; then
    echo -e "${BLUE}Shutting down Docker containers...${RESET}"
    docker-compose down -v
    echo -e "${GREEN}✔ Containers stopped and volumes removed.${RESET}"

    echo -e "${BLUE}Rebuilding and starting containers...${RESET}"
    docker-compose up -d --build
    echo -e "${GREEN}✔ Containers are up and running.${RESET}"
else
    echo -e "${RED}❌ Operation canceled.${RESET}"
fi
