## Здесь будут размещены все источники, которые помогли в создании данного приложения.

## Все источники будут поделены на пять частей: YouTube-плейлисты, статьи, CodeEx (Code Example), книги.

# YouTube-плейлисты

- [MAS](https://youtube.com/playlist?list=PLdHGtDv8nKT4jmZ-_LECa5v8e41W1Dmo_&si=zL_exk802DGhBNb6)
- [AI-Tools](https://youtube.com/playlist?list=PLdHGtDv8nKT64zFVkf4gNgtsAq3ECWEzY&si=NdjbAV-OZ81TCx7Y)

# Статьи

- The Rise and Potential of Large Language Model Based Agents: A Survey
  [[arXiv](https://arxiv.org/abs/2309.07864)]
    <details><summary>Summary</summary>
    
  1.  Вся информация в статье до параграфа №4 (стр.24) представляет из себя
      краткий обзор, который включает в себя: эволюцию AI-агентов, концепцию
      AI-агентов `(brain, perception, action)`, виды AI-агентов (для нас
      актуальны только LLM-Based AI-агенты и в параграфе 4 речь будет идти
      только о них), разбор составных частей AI-агента из концепции, очень общий
      обзор инструментов и техник для работы с AI-агентами. В самом конце
      затрагивается тема _Embodied actions_ - это техники, позволяющие
      AI-агентам физически взаимодействовать с окружающей средой.
  2.  В параграфе №4 освещаются следующие темы
      - типология приложений LLM-Based AI-агентов
        `(необходимо прочитать статьи, которые заявлены на Figure 6, здесь в т.ч. есть примеры  реализованных AI-агентов)`
      - цели, которых ожидается достичь при использовании AI-агентов (если
        корокто - то снять лишнюю рутинную нагрузку с человека и помочь ему
        эффективней использовать использовать свой научный и производственный
        потенциал)
      - вводят сценарии использования AI-агентов
        `(single agent, agent-agent, human-agent)`
      - обзор современных приложений агентов на базе LLM, дающий общее
        представление о практических сценариях развертывания.
      - `AutoGPT - MAS с открытым исходным кодом`
        [[GitHub](https://github.com/Significant-Gravitas/AutoGPT)]. Платформа
        для создания, развертывания и управления непрерывно работающими
        ИИ-агентами, автоматизирующими сложные рабочие процессы.
      - `Mind2Web - AI-Agent for Web Scenarios.`
        [[GitHub](https://osu-nlp-group.github.io/Mind2Web/)]
      - В параграфе 4.2 впервые упоминается `MAS`
      - `Cooperative Interaction for Complementarity which may be Disordered or Ordered` -
        при кооперативном взаимодействии агенты сотрудничают либо
        неупорядоченным, либо упорядоченным образом для достижения общих целей.
        См Figure 6.
      - `Adversarial Interaction for Advancement` - диалог между двумя и более
        агентами в процессе которого происходит рождение новых знаний и принятие
        решений. В конкурентной среде агенты могут быстро корректировать
        стратегии посредством динамических взаимодействий, стремясь выбрать
        наиболее выгодные или рациональные действия в ответ на изменения,
        вызванные другими агентами См Figure 6.
      - `Two paradigms of human-agent interaction`. In the
        `instructor-executor paradigm`, humans provide instructions or feedback,
        while agents act as executors. In the `equal partnership paradigm`,
        agents are human-like, able to engage in empathetic conversation and
        participate in collaborative tasks with humans.
      - `Quantitative feedback`
      - `Qualitative feedback`
  3.  В параграфе №5 анализируется поведение отдельных AI-агентов как внутри
  общества AI-агентов, так и персональное поведение вне общества. А также
  анализируется поведение агентов в разрезе различный сред. Этот параграф про
  "психологию AI-агентов". Это довольно интересная тема и там есть ссылка на
  множества статей с различными исследованиями в этой области. Освещаются
  следующие темы: - Поведение и личностные особенности AI-агентов. - Вводится
  классификация различных сред, в которых агенты могут осуществлять свое
  поведение и вступать во взаимодействие - Обсуждение того, как работает
  сообщество агентов, какие идеи люди могут извлечь из него, и о рисках, о
  которых могут возникнуть. -
  `На иллюстрации Figure 11 приводятся примеры различный AI-agents фреймворков`
  </details>

- AstroAgents: A Multi-Agent AI for Hypothesis Generation from Mass Spectrometry
  Data [[arXiv](https://arxiv.org/abs/2503.23170) |
  [GitHub](https://astroagents.github.io/)]
- Measuring Mathematical Problem Solving With the MATH Dataset
  [[arXiv](https://arxiv.org/abs/2103.03874)]
  <details><summary>Summary</summary>

  1.  В параграфах №1 и №2 освещаются следующие темы: \* Говорится про Asymptote
  Language с помощью которого можно решать геометрические задачи.
  </details>

- AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation
  [[arXiv](https://arxiv.org/abs/2308.08155)]
- Distilling Tool Knowledge into Language Models via Back-Translated Traces
  [[arXiv](https://arxiv.org/abs/2506.19171)]
- From LLM Reasoning to Autonomous AI Agents: A Comprehensive Review
  [[arXiv](https://arxiv.org/abs/2504.19678)] - _в этой статье есть обзорный
  список большого числа метрик для LLM в различных прикладных задачах, в т.ч. и
  математических. Также есть обзор метрик для AI-агентов. ОБЯЗАТЕЛЬНО К
  ПРОЧТЕНИЮ!_
- MACM: Utilizing a Multi-Agent System for Condition Mining in Solving Complex
  Mathematical Problems [[arXiv](https://arxiv.org/abs/2404.04735)]
- MathChat: Converse to Tackle Challenging Math Problems with LLM Agents
  [[arXiv](https://arxiv.org/abs/2306.01337)]
- X-MAS: Towards Building Multi-Agent Systems with Heterogeneous LLMs
  [[arXiv](https://arxiv.org/abs/2505.16997)]
- Solving Math Word Problems via Cooperative Reasoning induced Language Models
  [[arXiv](https://arxiv.org/abs/2210.16257)]
- Chain-of-Experts: When LLMs Meet Complex Operations Research Problems
  [[OpenReview](https://openreview.net/forum?id=HobyL1B9CZ)]
- MAPS: A Multi-Agent Framework Based on Big Seven Personality and Socratic
  Guidance for Multimodal Scientific Problem Solving
  [[arXiv](https://arxiv.org/abs/2503.16905)]
- MathBERT: A Pre-Trained Model for Mathematical Formula Understanding
  [[arXiv](https://arxiv.org/abs/2105.00377)]
- WizardMath: Empowering Mathematical Reasoning for Large Language Models via
  Reinforced Evol-Instruct [[arXiv](https://arxiv.org/abs/2308.09583) |
  [GitHub](https://wizardlm.github.io/WizardMath/)]
- Evaluation of LLMs for mathematical problem solving
  [[arXiv](https://www.semanticscholar.org/paper/Evaluation-of-LLMs-for-mathematical-problem-solving-Wang-Wang/4fa1e4442dc9c4bf8c5b2109955d28f066fd6991)]
  <details><summary>Summary</summary>

  1.  В статье оценивают способность LLM решать математические задачи.
  2.  Для эксперимента используют следющие LLM: GPT-4o; DeepSeek; Gemini.
  3.  Эксперимент проводится в разрезе трех датасетов с математическими
      задачами:

          - **GSM8K** - This dataset was released by OpenAI, which contains 8,500 application-based problems at the elementary and middle school levels. The language is colloquial, and the solution paths typically range from multiple steps, making it suitable for testing a model’s ability to process basic mathematical language and logic.
          - **MATH 500** - This dataset has 500 different difficulty and domain questions selected from the MATH benchmark, covering algebra, sequences, geometry, functions, and other fields. The question stems are close to academic teaching materials, with long chains of reasoning, suitable for analysing multi-step thinking abilities.
          - **University Graduate Question Bank** - This dataset consists of exam and assignment questions covering probability inference, matrix decomposition, optimisation theory, and financial computation, which are from the MIT Open Courseware. The language is rigorous, and the expression style is academic. Some questions have open structures, conceptual explanations, and non-standard expressions.

      </details>

- MathLearner: A Large Language Model Agent Framework for Learning to Solve
  Mathematical Problems [[arXiv](https://arxiv.org/abs/2408.01779)]
  <details><summary>Summary</summary>

  1. MathLearner - framework inspired by the principles of human learning,
     particularly inductive reasoning. Human learning often involves inferring
     general principles or solutions from specific examples and applying this
     knowledge to novel situations. Similarly, MathLearner aims to empower LLMs
     to learn to resolve math problems by leveraging inductive reasoning
     principles.
  2. MathLearner operates in three main stages, mirroring the stages of human
     learning:
     - **Learning from Examples:** The framework begins by exposing the LLM to a
       diverse set of math problems and their solutions, allowing it to learn
       from annotated examples.
     - **Memorizing Solving Methods:** MathLearner then focuses on memorizing
       various problem-solving methods and techniques, enabling the LLM to build
       a repository of strategies for tackling different types of math problems.
       approach problem-solving in a more systematic and structured manner.
     - **Recalling Previous Knowledge:** Finally, MathLearner equips the LLM
       with the ability to recall and apply its learned knowledge to solve new
       math problems, mimicking the process of retrieving and applying
       previously learned solutions.
  3. **MATH Hendrycks** - dataset that used for train and test.
  4. This paper presents several key contributions:
     - We propose a new retrieval method based on features to retrieve solutions
       to similar problems for the encountered problem.
     - We design a learning framework which can effectively reuse previously
       learned knowledge to solve current problems.
  5. Parsel [[GitHub](https://github.com/ezelikman/parsel)] - natural language
  framework for writing programs for any target language using code language
  models. Parsel considers multiple implementations for each function, searching
  sets of implementations to find programs passing unit tests (more generally,
  program constraints). It can be used for many kinds of algorithmic tasks, e.g.
  code synthesis, robotic planning, and theorem proving.
  </details>

- Mathematical Language Models: A Survey
  [[arXiv](https://arxiv.org/abs/2312.07622)] - _здесь приводится ошбирный обзор
  всего того, что связано с решением математических задач с помощью LLM.
  ОБЯЗАТЕЛЬНО К ПРОЧТЕНИЮ!_
  <details><summary>Summary</summary>

  1. В этом обзоре сравнивается множество LM для решения математических задач на
     **_60 математических датасетах_**!
  2. PLMs such as BERT, RoBERTa, BART, GPT-1 and GPT-2 undergo pretraining on
     extensive textual corpora to assimilate worldly knowledge. To enhance
     mathematical performance, certain endeavors focus on either pre-training or
     fine-tuning PLMs using mathematical datasets.
  3. Moreover, openly accessible LLMs are specifically designed for mathematical
     tasks, such as LLEMMA, Qwen-Math and InternLM-Math. Recently, o1 and o3
     obtained state-of-the-art performance on mathematical reasoning by
     integrating reinforcement learning with the Monte Carlo tree.
  4. DL4MATH (Deep Learning for Mathematical Reasoning)
     [[GitHub](https://github.com/lupantech/dl4math)]
  5. Awesome LLM4Math
     [[GitHub](https://github.com/tongyx361/Awesome-LLM4Math?tab=readme-ov-file)] -
     репозиторий с большим числом датасетов с данными по математическим задачам.
  6. MLM (Mathematical Language Models).
  7. На рисунке №1 представлены различные MLM для разных типов математических
     задач, от арифметического счета до доказательства теорем.
  8. На странице 3 авторы пишут, что существующие инструменты для решения
     математических задач они подразделяют на:
     - PLM-based (Pretrained Language Model) approaches: autoregression,
       non-autoregression.
     - LMs and LLMs-based methodologies: instruction learning; tool-based
       strategies; fundamental CoT techniques; advanced CoT methodologies;
       multi-modal methods.
     - MLM models
  9. На странице 3 авторы пишут, что подразделяют математические задачи на
     следующие виды:
     - mathematical calculations, consisting of arithmetic representation and
       arithmetic calculation;
     - mathematical reasoning, consisting of math problem-solving and theorem
       proving.
  10. На рисунке 3 показаны различные LLM и PLM для решения математических
  задач.
  </details>

- LLM Agents Making Agent Tools [[arXiv](https://arxiv.org/abs/2502.11705)]
- Math-Shepherd: Verify and Reinforce LLMs Step-by-step without Human
  Annotations [[arXiv](https://arxiv.org/abs/2312.08935)]
- A Comprehensive Review of AI Agents: Transforming Possibilities in Technology
  and Beyond [[arXiv](https://arxiv.org/abs/2508.11957)]
- A Survey on Code Generation with LLM-based Agents
  [[arXiv](https://arxiv.org/abs/2508.00083)]
- Multi-Agent Collaboration Mechanisms: A Survey of LLMs
  [[arXiv](https://arxiv.org/abs/2501.06322)]
- AgentGym-RL: Training LLM Agents for Long-Horizon Decision Making through
  Multi-Turn Reinforcement Learning [[arXiv](https://arxiv.org/abs/2509.08755) |
  [GitHub](https://github.com/WooooDyy/LLM-Agent-Paper-List?tab=readme-ov-file)]
- Multi-Agent Collaboration: Harnessing the Power of Intelligent LLM Agents
  [[arXiv](https://arxiv.org/abs/2306.03314)]
- Обзор Llemma: новая математическая open-source модель
  [[Хабр](https://habr.com/ru/companies/mts_ai/articles/771476/)]
  <details><summary>Summary</summary>
  1. Также оценка проводилась с помощью `majority voting или maj@k`. Это способ
     выбора самого популярного ответа среди k сгенерированных ответов, вместо
     greedy decoding, который просто выбирает самый вероятный. На рисунке ниже
     показан пример.
  2. Дополнительно я провела свою оценку на 21 задаче из ЕГЭ по профильной
  математике, сравнивая модель с ChatGPT и GPT-4. В результате Llemma показала
  худшие результаты. В защиту хотелось бы сказать, что тестирование проводилось
  на маленькой модели. Также цель авторов статьи заключалась в создании открытой
  базовой модели, которую лучше дообучить на определенной сфере математики.
  </details>

# CodeEx

- CAMEL: Communicative Agents for "Mind" Exploration of Large Language Model
  Society [[arXiv](https://arxiv.org/abs/2303.17760)]
- MASLab: A Unified and Comprehensive Codebase for LLM-based Multi-Agent Systems
  [[arXiv](https://arxiv.org/abs/2505.16988) |
  [GitHub](https://github.com/MASWorks/MASLab)]
- Agentic AI for Intent-Based Industrial Automation
  [[arXiv](https://arxiv.org/abs/2506.04980)] - _здесь приводится обзор
  различных репозиториев с примерами по разработке AI-агентов. На основе этой
  статьи я нашел все фреймворки ниже_
- LangChain
  [[Docs](https://docs.langchain.com/?_gl=1*ljs3o5*_gcl_au*MTQyNTE4OTUwNy4xNzYwOTAwMjUz*_ga*MTM3ODU4MjU3Ny4xNzYwOTAwMjU0*_ga_47WX3HKKY2*czE3NjA5MDAyNTMkbzEkZzEkdDE3NjA5MDAyOTMkajM4JGwwJGgw)] -
  _the platform for agent engineering_
- CrewAI [[Docs](https://docs.crewai.com/) |
  [GitHub](https://github.com/crewAIInc/crewAI)]
- Smolagents [[Hugging Face](https://huggingface.co/docs/smolagents/index) |
  [Docs](https://smolagents.org/docs/)] - _AI Agent Framework from Hugging Face_
- Agent Development Kit [[GitHub](https://google.github.io/adk-docs/)] - _AI
  Agent Framework from Google_

# Датасеты

- Сборники задач на русском языке [[problems.ru\]](https://problems.ru/)
- Сборники задач на английском языке
  [[hendrycks-math-dataset](https://github.com/hendrycks/math?tab=readme-ov-file)
  |
  [google-deepmind-math-dataset](https://github.com/google-deepmind/mathematics_dataset)]

# Книги | Курсы

- Antonio Gulli. Agentic Design Patterns: A Hands-On Guide to Building
  Intelligent Systems Antonio Gulli
  [[Английский-Source](https://docs.google.com/document/d/1rsaK53T3Lg5KoGwvf8ukOUvbELRtH-V0LnOIFDxBryE/preview?tab=t.0)
  | [Английский-in-PDF](https://t.me/alexgladkovblog/5820) |
  [Русский](https://github.com/pridees/agentic-design-patterns-book-rus?tab=readme-ov-file)]
- Chip Huyen. AI Engineering: Building Applications with Foundation Models
  [[PDF](https://t.me/Artifical_Intelligence_25/2086)]
- Agentic AI Crash Course
  [[GitHub](https://github.com/aishwaryanr/awesome-generative-ai-guide/tree/main/free_courses/agentic_ai_crash_course)]
- Agent Skills for Context Engineering
  [[GitHub](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)]
- LangChain Academy [[GitHub](https://academy.langchain.com/collections?page=2)]
- Chip Huyen. Agents
  [[Chip Huyen Blog](https://huyenchip.com/2025/01/07/agents.html)]

# Заметки

- What kind of metrics to measure the level of hallucinations there are?
- In-context Learning (ICL)
- The methods for agents to learn to utilize tools primarily consist of learning
  from demonstrations and learning from feedback.
- Embodied actions (воплощенные действия) — это действия, которые выполняются
  физическим или виртуальным телом (агентом) в окружающей среде, с учетом
  ограничений и возможностей этого тела. Примеры: физический робот-манипулятор,
  автономный автомобиль, всякие роботы Boston Dynamics.
- [`AutoGPT - MAS с открытым исходным кодом`](https://github.com/Significant-Gravitas/AutoGPT).
  Платформа для создания, развертывания и управления непрерывно работающими
  ИИ-агентами, автоматизирующими сложные рабочие процессы.
- Asymptote Language - язык, с помощью которого можно представлять
  геометрические задачи в виде текста. Впервые встретил упоминание этого языка
  [в этой статье](https://arxiv.org/abs/2103.03874).

---

Возможно следует создать отдельный топик со всеми AI-agent Framework'ами, чтобы
просто был небольшой обзор какие вообще продукты бывают.

Ниже представлены встречавшиеся мне по ходу прочтения материалы фреймворки:

- ChatLLM network
- AgentVerse [[GitHub](https://github.com/OpenBMB/AgentVerse)]
- MetaGPT [[GitHub](https://github.com/FoundationAgents/MetaGPT)]
- PaLM-E: An Embodied Multimodal Language Model
  [[GitHub](https://palm-e.github.io/)]
