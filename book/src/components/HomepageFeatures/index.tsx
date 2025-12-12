import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Chapter 1: Physical AI Foundations',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        Learn the fundamentals of Physical AI, including key characteristics like embodiment, perception, reasoning, and action. Explore humanoid robotics and the advantages of designing robots with human-like form factors.
      </>
    ),
  },
  {
    title: 'Chapter 2: Control & Hardware',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Master control systems including PID tuning, feedback loops, and stability analysis. Study sensors and actuators that enable robots to perceive and act in their environment.
      </>
    ),
  },
  {
    title: 'Chapter 3: Mechanical Design & Motion',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        Understand kinematic design, bipedal walking principles, and motion planning algorithms. Explore mechanical structures that enable humanoid robots to move and interact with the world.
      </>
    ),
  },
  {
    title: 'Chapter 4: Human-AI Collaboration',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        Explore safety, communication, and trust in human-robot interaction. Learn about ethical considerations and the future trajectory of physical AI and humanoid robotics.
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
