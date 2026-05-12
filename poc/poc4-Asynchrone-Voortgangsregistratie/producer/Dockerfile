FROM node:20-alpine
WORKDIR /app
COPY package.json .
RUN npm install --omit=dev
COPY producer.js .
EXPOSE 3000
CMD ["node", "producer.js"]
